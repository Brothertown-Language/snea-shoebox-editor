# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""RED-phase edge-input test for Issue #1400 Phase 2 Item 7 (SC-5).

Asserts that when ALL ranked scores fall below the calibrated default floor
``CALIBRATED_FLOOR`` = 0.93 (``src/services/semantic_search_service.py``),
``search_semantic(threshold=None)`` returns:

1. ``status == "ok"``
2. empty ``results``
3. the PINNED deficiency message EXACTLY
   ``"No gloss results meet the sensitivity floor."`` — the pinned constant
   from spec SC-5, not an example message.

The expected RED premise (plan Item 7): the test FAILS because the seam's
below-floor/empty-results branch currently returns the generic message
``"No matches above the configured threshold."`` for below-floor outcomes —
this exact mismatch was observed in the SC-8a RED and post-regression runs.

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

# Spec SC-5 pins this message text EXACTLY — a pinned constant, not an example.
PINNED_DEFICIENCY_MESSAGE = "No gloss results meet the sensitivity floor."

# The generic message the seam currently serves for below-floor outcomes
# (observed in the SC-8a RED and post-regression runs) — the RED premise.
GENERIC_MESSAGE_CURRENT = "No matches above the configured threshold."

# Query vector: unit vector along the principal axis.
E_QUERY = [1.0] + [0.0] * 383

# A fixture vector with cosine strictly below the calibrated default floor:
# [c, sqrt(1 - c^2), 0, ...] has cosine exactly c against E_QUERY.
COS_BELOW_FLOOR = 0.90  # strictly below CALIBRATED_FLOOR (0.93)


def _axis_vector(cosine):
    return [cosine, math.sqrt(1.0 - cosine * cosine)] + [0.0] * 382


E_BELOW = _axis_vector(COS_BELOW_FLOOR)


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


class TestSemanticBelowFloorMessageSc5Red(unittest.TestCase):
    """Issue #1400 Phase 2 Item 7 (SC-5, behavioral): pinned deficiency message."""

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

    def test_all_below_floor_returns_pinned_deficiency_message(self):
        """SC-5: all-below-floor outcome is ok + empty + PINNED message.

        Every fixture row scores strictly below CALIBRATED_FLOOR, so under
        ``threshold=None`` zero rows survive the floor filter. The seam must
        return ``status="ok"`` with empty results and the pinned deficiency
        message text EXACTLY as spec'd — not the generic
        ``"No matches above the configured threshold."`` message.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_BELOW])
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(
                result.status,
                "ok",
                "the all-below-floor outcome must return status='ok' "
                f"(got {result.status!r}, message {result.message!r})",
            )
            self.assertEqual(
                result.results,
                [],
                "the all-below-floor outcome must serve no ranked results "
                f"(got {result.results!r})",
            )
            self.assertEqual(
                result.message,
                PINNED_DEFICIENCY_MESSAGE,
                "the all-below-floor outcome must carry the PINNED deficiency "
                f"message exactly {PINNED_DEFICIENCY_MESSAGE!r}; the seam "
                f"currently returns {result.message!r} (the generic message "
                f"{GENERIC_MESSAGE_CURRENT!r}) for below-floor outcomes",
            )

    def test_all_below_floor_message_is_not_the_generic_message(self):
        """SC-5: the below-floor message differs from the legacy generic text.

        Guard against the observed mismatch: the pinned SC-5 message is a
        distinct constant, so an outcome carrying the generic
        ``"No matches above the configured threshold."`` message is a defect.
        """
        self.svc.set_query_encoder(_StubEncoder(E_QUERY))
        with self._txn() as conn:
            self._seed_rows(conn, [E_BELOW])
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(
                mode="gloss", query="x", threshold=None
            )
            self.assertEqual(result.results, [])
            self.assertNotEqual(
                result.message,
                GENERIC_MESSAGE_CURRENT,
                "the below-floor outcome must not carry the legacy generic "
                f"message {GENERIC_MESSAGE_CURRENT!r} — the pinned SC-5 "
                f"message is a distinct constant (got {result.message!r})",
            )


if __name__ == "__main__":
    unittest.main()
