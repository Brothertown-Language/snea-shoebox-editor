# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-7 (behavioral) RED test: search_semantic() degraded status edge matrix.

Asserts the degraded legs of ``src/services/semantic_search_service.py``
``search_semantic()`` against the freshly synced local DB. Every input in the
matrix must yield the designated status+message payload — never an exception:

1. Empty/whitespace query -> ``empty_query``, checked BEFORE any model
   invocation (a poison encoder that raises if called proves the guard
   ordering).
2. No embedded rows in either table -> ``no_embeddings`` for both modes, and
   the message names the admin backfill remedy.
3. Embedded rows exist exclusively under a non-pinned ``embedding_model`` ->
   ``stale_model`` (not no_embeddings), with the remedy message.
4. All scores below the threshold -> ``ok`` with empty results.

Fixture rows are transaction-scoped (rolled back at connection context exit),
so the synced dataset is untouched. The service is wired to the test
transaction via a connection shim so its own-session SQL observes the
uncommitted fixture rows.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import unittest

from sqlalchemy import create_engine, text

from src.database.connection import get_db_url

PIN = "thenlper/gte-small"
STALE = "stale-model-v0"

E_POS = [1.0] + [0.0] * 383
PERP = [0.0] + [1.0] + [0.0] * 382


class _PoisonEncoder:
    """Encoder that fails the test the moment the service invokes the model."""

    def encode(self, texts):
        raise AssertionError("model invocation must not happen for this input")


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


class TestSemanticSearchEdgeMatrixSc7(unittest.TestCase):
    """Phase 5 Item 7 (SC-7, behavioral): degraded status edge matrix."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc  # noqa: PLC0415

        cls.svc = svc
        cls.engine = create_engine(get_db_url())
        # Stashed in a tuple: a bare class-attribute function would bind into a
        # bound method when read back through `self.` (descriptor protocol),
        # turning the service's `_get_engine()` call into a self-passing call.
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

    def _make_record(self, conn):
        # Production DDL uses plain integer id columns (ids synchronized with
        # ``\\nt Record: <id>`` in raw MDF), so the synced local DB carries no
        # nextval column defaults. Fixture inserts assign ids explicitly from
        # the pre-existing sequences (created by migration 20260415000000).
        return int(
            conn.execute(
                text(
                    "INSERT INTO records "
                    "(id, lx, source_id, status, mdf_data, current_version, is_deleted) "
                    "VALUES (nextval('records_id_seq'), 'sc7-edge-lx', "
                    "(SELECT id FROM sources LIMIT 1), 'draft', '{}', 1, false) "
                    "RETURNING id"
                )
            ).scalar_one()
        )

    def _seed_gloss_rows(self, conn, rid, rows):
        conn.execute(
            text(
                "INSERT INTO gloss_search_entries "
                "(id, record_id, term, normalized_term, embedding, entry_type, embedding_model) "
                "VALUES (nextval('gloss_search_entries_id_seq'), :rid, :t, lower(:t), "
                "CAST(:emb AS vector), 'ge', :model)"
            ),
            [
                {"rid": rid, "t": t, "emb": str(emb), "model": model}
                for t, emb, model in rows
            ],
        )

    # --- edge 1: empty / whitespace -> empty_query, never a model call ------

    def test_empty_and_whitespace_query_status_pre_model(self):
        """Empty/whitespace queries produce empty_query without model invocation."""
        self.svc.set_query_encoder(_PoisonEncoder())
        self.svc._get_engine = lambda: (_ for _ in ()).throw(
            AssertionError("DB must not be touched for an empty query")
        )
        try:
            for q in ["", " ", "   ", "\t", "\n  "]:
                with self.subTest(query=repr(q)):
                    result = self.svc.search_semantic(mode="gloss", query=q)
                    self.assertIsInstance(
                        result, self.svc.SemanticSearchResult, "never an exception"
                    )
                    self.assertEqual(
                        result.status,
                        "empty_query",
                        "empty/whitespace query -> empty_query (pre-model)",
                    )
                    self.assertEqual(result.results, [])
                    self.assertIsInstance(result.message, str)
        finally:
            self.svc.set_query_encoder(None)

    # --- edge 2: no embedded rows in either table -> no_embeddings ----------

    def test_no_embeddings_when_no_embedded_rows_gloss_mode(self):
        """Zero embedded rows (gloss mode) -> no_embeddings + backfill remedy."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            # The synced DB carries real pinned rows; the "no embedded rows"
            # state is observed transaction-scoped (restored by rollback).
            conn.execute(text("DELETE FROM semantic_search_entries"))
            conn.execute(text("DELETE FROM gloss_search_entries"))
            self._make_record(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="probe")
        self.assertIsInstance(result, self.svc.SemanticSearchResult, "never an exception")
        self.assertEqual(
            result.status, "no_embeddings", "no embedded rows -> no_embeddings"
        )
        self.assertEqual(result.results, [])
        self.assertIn(
            "backfill",
            result.message.lower(),
            "no_embeddings message must name the admin backfill remedy",
        )

    def test_no_embeddings_when_no_embedded_rows_all_mode(self):
        """Zero embedded rows across BOTH tables -> no_embeddings + remedy."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            conn.execute(text("DELETE FROM semantic_search_entries"))
            conn.execute(text("DELETE FROM gloss_search_entries"))
            self._make_record(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="all", query="probe")
        self.assertEqual(result.status, "no_embeddings")
        self.assertEqual(result.results, [])
        self.assertIn(
            "backfill",
            result.message.lower(),
            "no_embeddings message must name the admin backfill remedy",
        )

    # --- edge 3: only stale-model rows -> stale_model ------------------------

    def test_stale_model_when_rows_exist_exclusively_under_stale_pin(self):
        """Embedded rows only under a non-pinned model -> stale_model + remedy."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            # Delete ALL rows (including the synced DB's pinned rows) so the
            # table content is exclusively the stale-model fixture rows;
            # restored by rollback.
            conn.execute(text("DELETE FROM semantic_search_entries"))
            conn.execute(text("DELETE FROM gloss_search_entries"))
            rid = self._make_record(conn)
            self._seed_gloss_rows(
                conn,
                rid,
                [("sc7-stale-a", E_POS, STALE), ("sc7-stale-b", E_POS, STALE)],
            )
            conn.execute(
                text(
                    "INSERT INTO semantic_search_entries "
                    "(id, record_id, entry_type, term, embedding, embedding_model) "
                    "VALUES (nextval('semantic_search_entries_id_seq'), :rid, 'ge', :t, "
                    "CAST(:emb AS vector), :model)"
                ),
                [
                    {"rid": rid, "t": "sc7-stale-sub", "emb": str(E_POS), "model": STALE},
                ],
            )
            self._wire_svc_to_txn(conn)
            for mode in ("gloss", "all"):
                with self.subTest(mode=mode):
                    result = self.svc.search_semantic(mode=mode, query="probe")
                    self.assertIsInstance(
                        result, self.svc.SemanticSearchResult, "never an exception"
                    )
                    self.assertEqual(
                        result.status,
                        "stale_model",
                        "rows exist but exclusively under a non-pinned model "
                        "-> stale_model (not no_embeddings)",
                    )
                    self.assertEqual(result.results, [])
                    self.assertIn(
                        "backfill",
                        result.message.lower(),
                        "stale_model message must name the admin backfill remedy",
                    )

    # --- edge 4: all scores below threshold -> ok with empty results --------

    def test_ok_with_empty_results_when_all_scores_below_threshold(self):
        """Pinned rows exist but all cosine scores fall below the threshold."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            rid = self._make_record(conn)
            self._seed_gloss_rows(conn, rid, [("sc7-perp", PERP, PIN)])
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="probe", threshold=0.5)
        self.assertEqual(
            result.status, "ok", "ranking leg ran and found nothing above threshold"
        )
        self.assertEqual(result.results, [], "all scores below threshold -> empty list")
        self.assertIsInstance(result.message, str)


if __name__ == "__main__":
    unittest.main()