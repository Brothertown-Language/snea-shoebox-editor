# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Edge-input test for Issue #1400 Phase 2 Item 9 (SC-7).

Revised SC-7 (spec-verbatim): "Whenever a threshold is active (the
calibrated default OR an explicit user threshold), rows scoring below the
active floor are excluded from the returned ``results`` — per-row filtering,
not just the all-below-floor edge case: under an explicit user threshold
with a PARTIALLY-below-floor score distribution, floor-clearing rows are
served in the same result set while below-floor rows are excluded from it
(the seam must never mix served and below-floor rows in one response)."

Covers the per-row filtering invariant on both active-threshold paths:

1. Default-path query (``threshold=None``) returns ONLY rows whose cosine
   is ``>= CALIBRATED_FLOOR`` (0.93).
2. Explicit user threshold with a MIXED corpus (one floor-clearing row +
   one below-floor row): floor-clearing rows are served in the same result
   set while below-floor rows are excluded from it — the seam never mixes
   served and below-floor rows in one response.
3. A mixed corpus under the default path returns EXCLUSIVELY
   floor-clearing rows.
4. Results are empty whenever ALL scores are below the floor.

The original RED premise (plan Item 9): the test FAILED because the default
floor did not yet apply in the SQL filter path — below-floor rows were
served as ranked results. GREEN was reached with per-row floor filtering.

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

# A fixture vector with cosine exactly c against E_QUERY:
# [c, sqrt(1 - c^2), 0, ...].
COS_BELOW_FLOOR = 0.90  # strictly below CALIBRATED_FLOOR (0.93)
COS_ABOVE_FLOOR = 0.97  # strictly above CALIBRATED_FLOOR (0.93)


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(COS_BELOW_FLOOR)
E_ABOVE = _axis_vector(COS_ABOVE_FLOOR)


class _StubEncoder:
    """encode()-compatible stub returning a fixed vector (SC-3 precedent)."""

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


class TestSemanticNoBelowFloorResultsSc7Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 9 (SC-7, behavioral): no below-floor noise."""

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

    def _run_default(self, vectors):
        """Seed rows, wire the service to the txn, run threshold=None search."""
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, vectors)
            self._wire_svc_to_txn(conn)
            return self.svc.search_semantic(mode="gloss", query="x", threshold=None)

    def _run_explicit(self, vectors, threshold):
        """Seed rows, wire the service to the txn, run explicit-threshold search."""
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, vectors)
            self._wire_svc_to_txn(conn)
            return self.svc.search_semantic(
                mode="gloss", query="x", threshold=threshold
            )

    def test_default_path_returns_only_floor_clearing_rows(self):
        """SC-7: threshold=None serves ONLY rows with cosine >= floor.

        A mixed corpus (0.97 above-floor + 0.90 below-floor) must return
        exclusively floor-clearing rows — the floor must actually apply in
        the SQL filter path for the default, not only for explicit thresholds.
        """
        result = self._run_default([E_ABOVE, E_BELOW])
        self.assertEqual(
            result.status,
            "ok",
            f"unexpected status {result.status!r} (message {result.message!r})",
        )
        self.assertGreater(
            len(result.results),
            0,
            "the floor-clearing fixture row must be served under the default path",
        )
        for record_id, score in result.results:
            self.assertGreaterEqual(
                score,
                self.floor,
                f"below-floor row served as a ranked result: "
                f"(record_id={record_id}, score={score}) < floor {self.floor} "
                "— the default floor does not apply in the SQL filter path",
            )

    def test_explicit_threshold_mixed_stub_serves_only_floor_clearing(self):
        """Revised SC-7: explicit threshold + PARTIALLY-below-floor stub.

        The spec-pinned evidence scenario: under an explicit user threshold
        with a mixed above/below-floor stub, floor-clearing rows are served
        in the same result set while below-floor rows are excluded from it —
        per-row filtering, not just the all-below-floor edge case. The seam
        must never mix served and below-floor rows in one response.
        """
        # Explicit user threshold of 0.95: the 0.97 row clears it, the 0.90
        # row does not. (An exact 0.97 cutoff is avoided because the DB
        # computes the cosine as 1 - (embedding <=> qv) in floating point.)
        result = self._run_explicit([E_ABOVE, E_BELOW], 0.95)
        self.assertEqual(
            result.status,
            "ok",
            f"unexpected status {result.status!r} (message {result.message!r})",
        )
        self.assertGreater(
            len(result.results),
            0,
            "floor-clearing rows must still be served under an explicit "
            "threshold with a partially-below-floor distribution",
        )
        served = set()
        for record_id, score in result.results:
            served.add(record_id)
            self.assertGreaterEqual(
                score,
                0.95,
                f"below-floor row served as a ranked result under an explicit "
                f"threshold: (record_id={record_id}, score={score}) < explicit "
                f"threshold 0.95 — the seam mixed served and "
                "below-floor rows in one response",
            )
        # Exactly one fixture row clears the explicit threshold (0.97); the
        # below-floor row (0.90) must be excluded from the same result set.
        self.assertEqual(
            len(served),
            1,
            f"expected exactly the floor-clearing row to be served under the "
            f"explicit threshold; got {len(served)} rows: {sorted(served)!r}",
        )

    def test_all_below_floor_returns_empty_results(self):
        """SC-7: results are empty whenever ALL scores are below the floor.

        Every fixture row scores strictly below CALIBRATED_FLOOR, so zero
        rows survive the floor filter — no below-floor row may appear as a
        ranked result under the default path.
        """
        result = self._run_default([E_BELOW])
        self.assertEqual(
            result.results,
            [],
            "results must be empty whenever all scores are below the floor "
            f"(got {result.results!r}) — below-floor rows are being served "
            "as ranked results under the default path",
        )


if __name__ == "__main__":
    unittest.main()
