# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase edge-input test for Issue #1400 Phase 2 Item 8 (SC-6).

Asserts the all-below-floor outcome NEVER raises an exception: the seam must
return normally (``status == "ok"``, no exception of any kind) across the
spec SC-6 edge-input matrix:

1. query matching nothing at all (no embedded rows in the closed world)
2. query matching only sub-floor rows (all scores strictly < CALIBRATED_FLOOR)
3. explicit threshold exactly equal to the floor (boundary case)
4. floor-clearing and below-floor fixture mix (partial survival)

Plan Item 8 RED premise: the test FAILS because the below-floor path is not
yet handled in the normal return flow. If the implementation already returns
normally for the whole matrix, the test passes immediately — ALREADY_GREEN
abort is then the honest observed terminal state.

Test harness proven pattern: test/test_semantic_below_floor_message_sc5_red.py
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


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(0.90)  # strictly below CALIBRATED_FLOOR
E_AT_FLOOR = _axis_vector(0.93)  # exactly at CALIBRATED_FLOOR
E_CLEAR = _axis_vector(0.95)  # floor-clearing anchor


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


class TestSemanticNoExceptionSc6Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 8 (SC-6, behavioral): no-exception matrix."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc  # noqa: PLC0415

        cls.svc = svc
        cls._original_get_engine = (svc._get_engine,)
        cls.floor = svc.CALIBRATED_FLOOR

    def setUp(self):
        self.engine = create_engine(get_db_url())
        self.svc._get_engine = self._original_get_engine[0]

    def tearDown(self):
        self.svc.set_query_encoder(None)
        self.svc._get_engine = self._original_get_engine[0]
        self.engine.dispose()

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

    def _closed_world(self, conn, vectors):
        """Insert pinned fixture rows in a CLOSED world (committed rows
        shadowed inside the rolled-back transaction); pass [] to empty it."""
        conn.execute(text("DELETE FROM semantic_search_entries"))
        conn.execute(text("DELETE FROM gloss_search_entries"))
        if not vectors:
            return None
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

    def _call_seam(self, vectors, threshold=None):
        """The seam must RETURN normally (no exception) for this input."""
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._closed_world(conn, vectors)
            self._wire_svc_to_txn(conn)
            return self.svc.search_semantic(
                mode="gloss", query="x", threshold=threshold
            )

    def test_query_matching_nothing_at_all_returns_normally(self):
        """SC-6: empty embedded world (query matches nothing at all) must
        return normally — no exception, a defined status (no_embeddings is
        itself a normal, defined return for this degenerate input)."""
        result = self._call_seam([])
        self.assertIn(
            result.status,
            ("ok", "no_embeddings"),
            f"undefined status for nothing-at-all world: {result.status!r}",
        )
        self.assertEqual(result.results, [])

    def test_query_matching_only_sub_floor_rows_returns_normally(self):
        """SC-6: only sub-floor rows in world — must return normally,
        status ok, empty results."""
        result = self._call_seam([E_BELOW])
        self.assertEqual(
            result.status,
            "ok",
            f"all-below-floor must return status='ok' (got {result.status!r})",
        )
        self.assertEqual(result.results, [])

    def test_threshold_exactly_equal_to_floor_returns_normally(self):
        """SC-6: explicit threshold exactly equal to the calibration floor —
        must return normally (no exception)."""
        result = self._call_seam([E_AT_FLOOR], threshold=self.floor)
        self.assertEqual(
            result.status,
            "ok",
            f"boundary input must return status='ok' (got {result.status!r})",
        )

    def test_mixed_floor_clearing_and_below_floor_returns_normally(self):
        """SC-6: mix of floor-clearing and sub-floor rows — must return
        normally with no exception."""
        result = self._call_seam([E_BELOW, E_CLEAR])
        self.assertEqual(
            result.status,
            "ok",
            f"mixed input must return status='ok' (got {result.status!r})",
        )
        scores = [s for _, s in result.results]
        if scores:
            self.assertTrue(
                all(s >= self.floor for s in scores),
                f"sub-floor rows leaked into results: {scores}",
            )


if __name__ == "__main__":
    unittest.main()
