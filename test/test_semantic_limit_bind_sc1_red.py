# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Issue #1399 SC-1 (behavioral) RED test: limit bind-param parity.

Calls ``search_semantic(mode="gloss", query="water", limit=5)`` (a real,
non-empty calibration-corpus query) against the local DB replica via the
proven stub-encoder + transaction-scoped fixture pattern. Asserts no
exception is raised — on current HEAD the run FAIL/ERRORs with
``sqlalchemy.exc.InvalidRequestError: A value is required for bind
parameter 'lim'`` because ``_candidate_sql`` renders ``LIMIT :lim`` while
``search_semantic`` never populates ``params["lim"]``.

Test lives in the owning (root) repo's ``test/`` directory per the
owning-repo principle; RED phase writes tests only.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import math
import unittest

from sqlalchemy import create_engine, text

from src.database.connection import get_db_url

PIN = "thenlper/gte-small"
E_POS = [1.0] + [0.0] * 383


def _mixed(first, second):
    """Unit 384-dim vector with the given first two components."""
    norm = math.sqrt(first * first + second * second)
    return [first / norm, second / norm] + [0.0] * 382


# Three distinct floor-clearing (>= CALIBRATED_FLOOR = 0.93) similarity
# scores so the unlimited ordering is deterministic and the limit=1 cap
# has a meaningful element to cut. Score equals the first component
# because the query vector is E_POS.
E_TOP = E_POS  # score 1.0
E_MID = _mixed(0.97, 0.24)  # score ~0.97
E_LOW = _mixed(0.95, 0.31)  # score ~0.95


class _StubEncoder:
    """Deterministic encode()-compatible stub returning a fixed vector."""

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


class TestSemanticLimitBindSc1Red(unittest.TestCase):
    """Issue #1399 Item 1 (SC-1, behavioral): limit=5 executes without error."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc  # noqa: PLC0415

        cls.svc = svc
        cls.engine = create_engine(get_db_url())
        # Stashed in a tuple: a bare class-attribute function would bind into
        # a bound method when read back through `self.` (descriptor protocol).
        cls._original_get_engine = (svc._get_engine,)

    def _wire_svc_to_txn(self, conn):
        class _EngineShim:
            def connect(self):
                return _ConnShim(conn)

        self.svc._get_engine = lambda: _EngineShim()

    def setUp(self):
        self.svc._get_engine = self._original_get_engine[0]

    def tearDown(self):
        self.svc.set_query_encoder(None)
        self.svc._get_engine = self._original_get_engine[0]

    def _seed_txn(self, conn):
        """Transaction-scoped fixture: wipe committed entries, seed 3 rows
        with distinct floor-clearing scores. Restored by rollback."""
        conn.execute(text("DELETE FROM semantic_search_entries"))
        conn.execute(text("DELETE FROM gloss_search_entries"))
        rid = int(
            conn.execute(
                text(
                    "INSERT INTO records "
                    "(id, lx, source_id, status, mdf_data, current_version, "
                    "is_deleted) VALUES (nextval('records_id_seq'), 'water-x', "
                    "(SELECT id FROM sources LIMIT 1), 'draft', '{}', 1, false) "
                    "RETURNING id"
                )
            ).scalar_one()
        )
        for vec in (E_TOP, E_MID, E_LOW):
            conn.execute(
                text(
                    "INSERT INTO gloss_search_entries "
                    "(id, record_id, term, normalized_term, embedding, entry_type, "
                    "embedding_model) VALUES "
                    "(nextval('gloss_search_entries_id_seq'), :rid, 'water', "
                    "lower('water'), CAST(:emb AS vector), 'ge', :model)"
                ),
                {"rid": rid, "emb": str(vec), "model": PIN},
            )
        return rid

    def test_limit_5_executes_without_exception(self):
        """search_semantic(mode='gloss', query='water', limit=5) never raises."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self.engine.connect() as conn:
            txn = conn.begin()
            try:
                # Transaction-scoped fixture: clear committed search-entry
                # rows and seed three pinned 'water' rows (distinct
                # floor-clearing scores) so the ranked leg runs and the
                # LIMIT :lim placeholder is exercised. Restored by
                # rollback — synced dataset untouched.
                self._seed_txn(conn)
                self._wire_svc_to_txn(conn)
                result = self.svc.search_semantic(
                    mode="gloss", query="water", limit=5
                )
                self.assertIsInstance(
                    result, self.svc.SemanticSearchResult, "no exception expected"
                )
                self.assertEqual(result.status, "ok")
            finally:
                txn.rollback()

    def test_limit_1_returns_top_ranked_pair_of_unlimited_ordering(self):
        """Issue #1399 Item 2 (SC-2, behavioral): limit=1 caps to exactly
        the top-ranked (record_id, score) pair of the unlimited ordering
        (score DESC, record_id ASC tie-break)."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self.engine.connect() as conn:
            txn = conn.begin()
            try:
                self._seed_txn(conn)
                self._wire_svc_to_txn(conn)
                unlimited = self.svc.search_semantic(
                    mode="gloss", query="water", limit=None
                )
                self.assertEqual(
                    unlimited.status,
                    "ok",
                    "unlimited baseline must be a ranked ok result",
                )
                self.assertEqual(
                    len(unlimited.results),
                    3,
                    "fixture seeds exactly 3 floor-clearing rows",
                )
                capped = self.svc.search_semantic(
                    mode="gloss", query="water", limit=1
                )
                self.assertEqual(capped.status, "ok")
                self.assertEqual(
                    len(capped.results),
                    1,
                    "limit=1 must cap results to exactly one pair",
                )
                self.assertEqual(
                    capped.results,
                    unlimited.results[:1],
                    "limit=1 pair must equal the top-ranked pair of the "
                    "unlimited ordering (score DESC, record_id ASC)",
                )
            finally:
                txn.rollback()

    def test_limit_none_path_unchanged_full_ranked_list(self):
        """Issue #1399 Item 3 (SC-3, behavioral): limit=None invariance guard.

        Asserts the limit=None path is unchanged by the fix: no LIMIT
        clause is emitted (full ranked list returned — count equals the
        recorded pre-fix baseline count), and ordering is unchanged
        between repeated unlimited calls. Invariant-preserving guard:
        the pre-fix state is unreachable on this branch (fix landed in
        f5f5d63) and limit=None never emitted LIMIT even pre-fix, so
        this test may pass immediately per the plan.
        """
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self.engine.connect() as conn:
            txn = conn.begin()
            try:
                self._seed_txn(conn)
                self._wire_svc_to_txn(conn)
                first = self.svc.search_semantic(
                    mode="gloss", query="water", limit=None
                )
                self.assertEqual(first.status, "ok")
                # Recorded pre-fix baseline count: the transaction-scoped
                # stub seeds exactly 3 floor-clearing rows, making the
                # unlimited count deterministic and equal pre- and
                # post-fix (no LIMIT clause on the limit=None path).
                self.assertEqual(
                    len(first.results),
                    3,
                    "limit=None must return the full ranked list — count "
                    "equals the recorded pre-fix baseline (3 seeded rows); "
                    "a count below baseline would indicate a LIMIT clause "
                    "regression on the unlimited path",
                )
                second = self.svc.search_semantic(
                    mode="gloss", query="water", limit=None
                )
                self.assertEqual(second.status, "ok")
                self.assertEqual(
                    first.results,
                    second.results,
                    "ordering of the unlimited ranked list must be "
                    "unchanged across calls",
                )
            finally:
                txn.rollback()


if __name__ == "__main__":
    unittest.main()
