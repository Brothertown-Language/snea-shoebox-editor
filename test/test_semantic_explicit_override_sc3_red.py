# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase seam test for Issue #1400 Phase 2 Item 5 (SC-3).

Asserts that an explicit ``threshold`` value passed by the caller overrides
the calibrated default floor ``CALIBRATED_FLOOR`` = 0.93
(``src/services/semantic_search_service.py``):

1. An explicit threshold BELOW the default floor must admit rows the default
   would exclude: a row at cosine 0.90 (below the 0.93 floor) is served when
   the caller passes threshold=0.80, and empty when threshold=None.
2. An explicit threshold ABOVE the default must exclude rows the default
   admits: a row at cosine 0.95 (above the 0.93 floor, served under
   threshold=None) is excluded when the caller passes threshold=0.97.

The expected RED premise (plan Item 5): the test FAILS because the
override-vs-default precedence is not yet distinguished.

Test harness proven pattern: test/test_semantic_default_floor_sc2_red.py
(deterministic axis vectors + transaction-scoped fixture rows + connection
shim wiring the service to the test transaction).

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import math
import unittest

from sqlalchemy import create_engine, text

from src.database.connection import get_db_url

PIN = "thenlper/gte-small"

# Query vector: unit vector along the principal axis.
E_QUERY = [1.0] + [0.0] * 383

# Fixture vectors with controlled cosine similarity to E_QUERY.
# A vector [c, sqrt(1 - c^2), 0, ...] has cosine exactly c against E_QUERY.
COS_BELOW_FLOOR = 0.90  # strictly below the calibrated default floor (0.93)
COS_ABOVE_FLOOR = 0.95  # strictly above the default floor, below 0.97

EXPLICIT_BELOW = 0.80  # explicit override below the default floor
EXPLICIT_ABOVE = 0.97  # explicit override above the default floor


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(COS_BELOW_FLOOR)
E_ABOVE_DEFAULT = _axis_vector(COS_ABOVE_FLOOR)


class _StubEncoder:
    """encode()-compatible stub returning a fixed vector (SC-5 precedent)."""

    def __init__(self, vector):
        self._vector = vector

    def encode(self, texts):
        _ = list(texts)
        return [list(self._vector)]


class _ConnShim:
    """Delegates service SQL into the caller's transaction connection."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        return self._conn.execute(sql, params)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestSemanticExplicitOverrideSc3Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 5 (SC-3, behavioral): explicit override wins."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc  # noqa: PLC0415

        cls.svc = svc
        cls.engine = create_engine(get_db_url())
        cls._original_get_engine = (svc._get_engine,)
        # The floor under test is the module-level named calibration constant.
        cls.floor = svc.CALIBRATED_FLOOR

    def setUp(self):
        self.svc._get_engine = self._original_get_engine[0]

    def tearDown(self):
        self.svc.set_query_encoder(None)
        self.svc._get_engine = self._original_get_engine[0]

    def _txn(self):
        """Transaction-scoped fixture context: always rolls back on exit."""
        from contextlib import contextmanager

        @contextmanager
        def ctx():
            with self.engine.connect() as conn:
                txn = conn.begin()
                try:
                    yield conn
                finally:
                    txn.rollback()
        return ctx()

    def _seed_rows(self, conn, vectors):
        """Insert pinned fixture rows with the given vectors; caller rolls back.

        Shadow committed search-entry rows first (closed fixture world — the
        synced DB carries real embedded rows), inside the rolled-back
        transaction so committed data is untouched.
        """
        conn.execute(text("DELETE FROM semantic_search_entries"))
        conn.execute(text("DELETE FROM gloss_search_entries"))
        rec = conn.execute(
            text(
                "INSERT INTO records "
                "(id, lx, source_id, status, mdf_data, current_version, is_deleted) "
                "VALUES (nextval('records_id_seq'), 'test-lx', "
                "(SELECT id FROM sources LIMIT 1), 'draft', '{}', 1, false) "
                "RETURNING id"
            )
        ).scalar_one()
        rid = int(rec)
        conn.execute(
            text(
                "INSERT INTO gloss_search_entries "
                "(id, record_id, term, normalized_term, embedding, entry_type, embedding_model) "
                "VALUES (nextval('gloss_search_entries_id_seq'), :rid, :term, lower(:term), "
                "CAST(:emb AS vector), 'ge', :model)"
            ),
            [
                {
                    "rid": rid,
                    "term": f"seed-fixture-{i}",
                    "emb": str(vec),
                    "model": PIN,
                }
                for i, vec in enumerate(vectors)
            ],
        )
        return rid

    def _wire_svc_to_txn(self, conn):
        class _EngineShim:
            def connect(self):
                return _ConnShim(conn)

        self.svc._get_engine = lambda: _EngineShim()

    def test_explicit_below_floor_admits_rows_default_excludes(self):
        """SC-3: an explicit threshold below the floor overrides the default.

        A row at cosine 0.90 is below CALIBRATED_FLOOR (excluded under
        threshold=None), but with an explicit threshold=0.80 the caller's
        value wins: the row must be served.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_BELOW])
            self._wire_svc_to_txn(conn)
            default_result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(
                default_result.results,
                [],
                "precondition: the 0.90 row must be excluded under the "
                f"default floor ({self.floor}); got {default_result.results!r}",
            )
            override_result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=EXPLICIT_BELOW
            )
            self.assertEqual(
                len(override_result.results),
                1,
                "an explicit threshold below the default floor must override "
                "the default and admit the 0.90 row the default excludes "
                f"(got {override_result.results!r})",
            )
            score = override_result.results[0][1]
            self.assertGreaterEqual(score, EXPLICIT_BELOW)

    def test_explicit_above_default_excludes_rows_default_admits(self):
        """SC-3: an explicit threshold above the default overrides it.

        A row at cosine 0.95 clears CALIBRATED_FLOOR (served under
        threshold=None), but with an explicit threshold=0.97 the caller's
        value wins: the row must be excluded (ok + empty results).
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_ABOVE_DEFAULT])
            self._wire_svc_to_txn(conn)
            default_result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(
                len(default_result.results),
                1,
                "precondition: the 0.95 row must be served under the default "
                f"floor ({self.floor}); got {default_result.results!r}",
            )
            override_result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=EXPLICIT_ABOVE
            )
            self.assertEqual(
                override_result.results,
                [],
                "an explicit threshold above the default floor must override "
                "the default and exclude the 0.95 row the default admits "
                f"(got {override_result.results!r})",
            )
            self.assertEqual(override_result.status, "ok")


if __name__ == "__main__":
    unittest.main()
