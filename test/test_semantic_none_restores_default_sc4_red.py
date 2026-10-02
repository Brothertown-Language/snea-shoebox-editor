# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase seam test for Issue #1400 Phase 2 Item 6 (SC-4).

Sticky-state guard: after a prior explicit-override call in the same
process, a ``threshold=None`` call must re-engage the calibrated default
floor ``CALIBRATED_FLOOR`` (``src/services/semantic_search_service.py``)
and behave identically to a fresh ``threshold=None`` call.

Sequence asserted (same process, same connection world):

1. Fresh ``threshold=None`` call: a row at cosine 0.90 (below the 0.93
   default floor) is excluded.
2. Explicit override ``threshold=0.80``: the same row is admitted
   (override wins — SC-3).
3. ``threshold=None`` again, after the override: the row must be excluded
   once more — identical to step 1. No sticky override state may survive
   the prior call.

The seam is a pure parameter-passing function (threshold is a parameter,
no module state), so if the implementation is per-call stateless this
test passes immediately — the ALREADY_GREEN abort applies.

Test harness proven pattern: test/test_semantic_explicit_override_sc3_red.py
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

# Fixture vector with controlled cosine similarity to E_QUERY.
# A vector [c, sqrt(1 - c^2), 0, ...] has cosine exactly c against E_QUERY.
COS_BELOW_FLOOR = 0.90  # strictly below the calibrated default floor (0.93)

EXPLICIT_BELOW = 0.80  # explicit override below the default floor


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(COS_BELOW_FLOOR)


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


class TestSemanticNoneRestoresDefaultSc4Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 6 (SC-4): None after override re-engages default."""

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

    def test_none_after_override_reengages_default_floor(self):
        """SC-4: threshold=None after an explicit override restores the default.

        The None call after the override must behave identically to a fresh
        None call: the 0.90 row is excluded again. A sticky override state
        would keep serving the row under the subsequent None call.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_BELOW])
            self._wire_svc_to_txn(conn)

            # 1. Fresh None call: row excluded by the default floor.
            fresh_none = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(
                fresh_none.results,
                [],
                "precondition: the 0.90 row must be excluded under a fresh "
                f"threshold=None call (floor {self.floor}); got "
                f"{fresh_none.results!r}",
            )

            # 2. Explicit override: row admitted (SC-3 precedence).
            override = self.svc.search_semantic(
                mode="gloss", query="x", threshold=EXPLICIT_BELOW
            )
            self.assertEqual(
                len(override.results),
                1,
                "precondition: the explicit override must admit the 0.90 "
                f"row; got {override.results!r}",
            )

            # 3. None after the override: default re-engaged — identical
            #    to the fresh None call (no sticky state).
            none_after = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(
                none_after.results,
                fresh_none.results,
                "threshold=None after an explicit override must behave "
                "identically to a fresh threshold=None call — no sticky "
                "override state may survive the prior call "
                f"(fresh: {fresh_none.results!r}, after: {none_after.results!r})",
            )
            self.assertEqual(
                none_after.results,
                [],
                "threshold=None after an explicit override must re-engage "
                "the calibrated default floor and exclude the 0.90 row; "
                f"got {none_after.results!r}",
            )


if __name__ == "__main__":
    unittest.main()
