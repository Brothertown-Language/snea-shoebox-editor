# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase seam test for Issue #1400 Phase 2 Item 4 (SC-2).

Asserts that ``search_semantic(threshold=None)`` filters on the module-level
calibrated default floor constant ``CALIBRATED_FLOOR``
(``src/services/semantic_search_service.py``):

1. A query whose top cosine score is below the calibrated floor returns the
   below-floor empty outcome (``status=ok`` with empty ``results``), NOT the
   full ranked list of below-floor rows.
2. A floor-clearing query's returned results all meet the floor (every
   score >= CALIBRATED_FLOOR), and the floor-clearing fixture row is served.

The test FAILS (RED) because ``threshold=None`` currently bypasses filtering
entirely and returns the full ranked list.

Test harness proven pattern: test/test_semantic_search_seam_sc5.py
(deterministic axis vectors + transaction-scoped fixture rows + connection
shim wiring the service to the test transaction).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
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
COS_BELOW_FLOOR = 0.90  # strictly below the calibrated floor (0.93)
COS_ABOVE_FLOOR = 0.99  # strictly above the calibrated floor


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(COS_BELOW_FLOOR)
E_ABOVE = _axis_vector(COS_ABOVE_FLOOR)


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


class TestSemanticDefaultFloorSc2Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 4 (SC-2, behavioral): default-on-None floor."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc  # noqa: PLC0415

        cls.svc = svc
        cls.engine = create_engine(get_db_url())
        cls._original_get_engine = (svc._get_engine,)
        # The seam must consume the module-level named calibration constant
        # (Phase 1 published it); the floor under test is that constant.
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

    def test_below_floor_query_returns_empty_under_default_none(self):
        """SC-2: threshold=None engages the calibrated floor.

        A query whose top cosine score (0.90) is below the calibrated floor
        must return the below-floor empty outcome (ok + empty results), NOT
        the full ranked list of below-floor rows.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_BELOW])
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="x", threshold=None)
            self.assertEqual(
                result.results,
                [],
                "threshold=None must filter on the calibrated default floor; "
                "a below-floor top score must yield empty results, not the "
                f"ranked list (got {result.results!r})",
            )
            self.assertEqual(result.status, "ok")

    def test_floor_clearing_query_results_all_meet_floor(self):
        """SC-2: a floor-clearing query's results all meet the floor.

        With rows at cosine 0.99 (above floor) and 0.90 (below floor), the
        default (threshold=None) must serve only the 0.99 row; every served
        score must be >= the calibrated floor.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_ABOVE, E_BELOW])
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="x", threshold=None)
            self.assertEqual(result.status, "ok")
            scores = [s for _, s in result.results]
            for score in scores:
                self.assertGreaterEqual(
                    score,
                    self.floor,
                    f"threshold=None must filter on CALIBRATED_FLOOR "
                    f"({self.floor}); below-floor row served at {score}",
                )
            self.assertEqual(
                len(result.results),
                1,
                "only the floor-clearing row must survive the default floor",
            )
            rec_ids = [r for r, _ in result.results]
            self.assertEqual(len(rec_ids), len(set(rec_ids)))


if __name__ == "__main__":
    unittest.main()
