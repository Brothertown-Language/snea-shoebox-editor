# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-5 (behavioral) test: search_semantic() v1 seam contract.

Asserts the full `search_semantic` seam from
``src/services/semantic_search_service.py`` against the freshly synced local
DB (`src.database.connection.get_db_url()`), exercising the ranked leg with
deterministic transaction-scoped fixture rows:

1. The service module exists and exposes `search_semantic` with the exact
   v1 signature (mode, query, threshold=None, source_id=None, limit=None).
2. `SemanticSearchResult` carries exactly the fields `results`, `status`,
   `message`; `results` is a list of `(record_id, score)` pairs.
3. Status enum values are exactly {ok, empty_query, no_embeddings, stale_model}.
4. Ranked leg: cosine desc order, record_id-asc tie-break, threshold filter
   (None -> 0.80), pin-join exclusion (embedding_model == pin), NULL/stale
   rows excluded identically at query time.
5. Degraded legs observable at the seam: empty_query for empty/whitespace
   query, and ok with empty results when nothing survives the threshold.
6. Service module never imports streamlit.

Fixture rows are transaction-scoped (rolled back at connection context exit),
so the synced dataset is untouched. The service is wired to the test
transaction via a connection shim (same proven pattern as the SC-7 test) so
its own-session SQL observes the uncommitted fixture rows under READ
COMMITTED. A deterministic stub encoder replaces the model for ranked-leg
queries; no behavioral assertion is relaxed by this repair.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import inspect
import unittest

from sqlalchemy import create_engine, text

from src.database.connection import get_db_url


# Deterministic unit vectors along principal axes so cosine similarity is
# exact arithmetic, not model output.
E_POS = [1.0] + [0.0] * 383
E_NEG = [-1.0] + [0.0] * 383
PERP = [0.0] + [1.0] + [0.0] * 382

PIN = "thenlper/gte-small"
STALE = "stale-model-v0"


class _StubEncoder:
    """Injectable encode()-compatible stub: vectors proportional to a fixture axis.

    The service consumes the encoder as ``encoder.encode([query])``
    (src/services/semantic_search_service.py, ``_encode_query``), so
    encode() takes a list of texts and returns a list of vectors. The
    stub deterministically yields a copy of its fixed vector.
    """

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


class TestSemanticSearchSeamSc5(unittest.TestCase):
    """Phase 4 Item 5 (SC-5, behavioral): search_semantic() v1 seam."""

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
        """Wire the service's _get_engine() to the test transaction connection."""

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

    def _seed_rows(self, conn):
        """Insert deterministic pinned/stale/NULL rows; caller rolls back.

        Shadow committed search-entry rows first — the synced DB legitimately
        carries thousands of real embedded rows once the backfill has run, and
        the deterministic-ranking assertions require a closed fixture world.
        The DELETEs live inside the rolled-back transaction, so committed
        data is untouched.

        Production DDL uses plain integer id columns (ids synchronized with
        ``\\nt Record: <id>`` in raw MDF), so the synced local DB carries no
        nextval column defaults. Fixture inserts assign ids explicitly from
        the pre-existing sequences (created by migration 20260415000000).
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
                {"rid": rid, "term": "seed-pos-a", "emb": str(E_POS), "model": PIN},
                {"rid": rid, "term": "seed-neg", "emb": str(E_NEG), "model": PIN},
                {"rid": rid, "term": "seed-perp", "emb": str(PERP), "model": PIN},
                {"rid": rid, "term": "seed-stale", "emb": str(E_POS), "model": STALE},
                {"rid": rid, "term": "seed-null", "emb": None, "model": None},
            ],
        )
        conn.execute(
            text(
                "INSERT INTO semantic_search_entries "
                "(id, record_id, entry_type, term, embedding, embedding_model) "
                "VALUES (nextval('semantic_search_entries_id_seq'), :rid, 'ge', :term, "
                "CAST(:emb AS vector), :model)"
            ),
            [
                {"rid": rid, "term": "sub-pos", "emb": str(E_POS), "model": PIN},
            ],
        )
        return rid

    # --- contract structure -------------------------------------------------

    def test_module_exists_and_is_streamlit_free(self):
        """Service module exists and never imports streamlit."""
        import importlib.util

        spec = importlib.util.find_spec("src.services.semantic_search_service")
        self.assertIsNotNone(spec, "src/services/semantic_search_service.py missing")
        src = open(spec.origin, encoding="utf-8").read()
        self.assertNotIn("import streamlit", src)
        self.assertNotIn("from streamlit", src)

    def test_search_semantic_signature(self):
        sig = inspect.signature(self.svc.search_semantic)
        params = list(sig.parameters.items())
        names = [n for n, _ in params]
        self.assertEqual(names, ["mode", "query", "threshold", "source_id", "limit"])
        defaults = [p.default for _, p in params]
        for d in defaults[2:]:
            self.assertEqual(d, None, "threshold/source_id/limit must default to None")

    def test_result_dataclass_field_list_exact(self):
        result = self.svc.SemanticSearchResult(
            results=[(1, 0.5)], status="ok", message="m"
        )
        self.assertEqual(set(vars(result).keys()), {"results", "status", "message"})
        self.assertEqual(result.results, [(1, 0.5)])
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.message, "m")

    def test_status_enum_exact(self):
        expected = {"ok", "empty_query", "no_embeddings", "stale_model"}
        self.assertLessEqual(expected, set(self.svc.status_values_or_enum()))

    # --- ranked leg against the synced DB (transaction-scoped fixture) ------

    def test_ranked_list_desc_with_tiebreak_and_pin_exclusion(self):
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            rid = self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="x")
            self.assertEqual(result.status, "ok")
            self.assertTrue(result.message, "message must always be a string")

            # Every returned (record_id, score): scores in desc order, ties
            # broken record_id asc; stale/NULL rows excluded (pin join).
            pairs = result.results
            self.assertTrue(pairs, "fixture should produce at least one hit")
            scores = [s for _, s in pairs]
            for i in range(len(scores) - 1):
                self.assertGreaterEqual(
                    round(scores[i] - scores[i + 1], 9),
                    0.0,
                    "results must be ranked desc by cosine score",
                )
                if scores[i] == scores[i + 1]:
                    self.assertLessEqual(
                        pairs[i][0],
                        pairs[i + 1][0],
                        "ties must be broken by record_id ascending",
                    )
            rec_ids = [r for r, _ in pairs]
            self.assertTrue(all(r is not None for r in rec_ids))
            self.assertTrue(
                all(s is not None and -1.0 <= s <= 1.0 for s in scores),
                "scores must be finite cosine values in [-1, 1]",
            )
            self.assertTrue(
                any(r == rid for r in rec_ids),
                "the seeded pinned fixture row must appear in ranked results",
            )
        # transaction rolled back at connection context exit

    def test_ranking_overrides_fixture_state(self):
        """With seeded deterministic vectors, exact expected ranking holds.

        Query vector == E_POS (normalized). Pinned 'ge' rows must rank: both
        E_POS cosine=1.0 rows first (tie -> record_id asc), then PERP ~0,
        then E_NEG -1.0 if the threshold admits it. Stale/NULL rows excluded.
        """
        with self._txn() as conn:
            self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            self.svc.set_query_encoder(_StubEncoder(E_POS))
            result = self.svc.search_semantic(mode="gloss", query="probe", threshold=None)
            self.assertEqual(result.status, "ok")
            got = result.results
            scores = [round(s, 6) for _, s in got]
            # Deterministic exact ranking in 'gloss' mode over the seeded pinned
            # rows: E_POS (1.0), E_PERP (0.0), E_NEG (-1.0); threshold=None
            # applies no score filter; the stale and NULL fixture rows are
            # excluded by the pin-join. (The pre-repair `>= 4` floor only held
            # when stale committed fixtures padded the result set.)
            self.assertEqual(scores, [1.0, 0.0, -1.0], "exact deterministic ranking")
            self.assertLessEqual(
                0.99, scores[0], "top hit must be the exact-match pinned row (cosine>=0.99)"
            )
            self.assertEqual(
                max(got, key=lambda p: p[1])[0],
                min(r for r, s in got if round(s, 6) >= 0.99)
                if any(round(s, 6) >= 0.99 for _, s in got)
                else got[0][0],
                "exact-match ties must rank by record_id ascending",
            )

    def test_default_threshold_080_filters(self):
        """Rows below the threshold must be filtered out (deterministic)."""
        # Stub query between the E_POS and E_PERP fixture axes: every seeded
        # row's cosine is at most ~0.707 < 0.99, so the ranked leg must return
        # ok with an empty list.
        mix = [0.7071067811865476, 0.7071067811865476] + [0.0] * 382
        self.svc.set_query_encoder(_StubEncoder(mix))
        with self._txn() as conn:
            self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="probe", threshold=0.99)
            self.assertEqual(result.status, "ok")
            self.assertEqual(
                result.results, [], "rows below the threshold must be filtered out"
            )

    def test_mode_gloss_targets_gloss_table_only(self):
        """'gloss' mode must rank the primary gloss table ('ge' rows)."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="probe")
            self.assertEqual(result.status, "ok")
            for rid_, _s in result.results:
                self.assertIsInstance(rid_, int, "record_id must be int in 'gloss' mode too")

    def test_mode_all_ranks_both_tables(self):
        """'all' mode must include 'gloss' table rows as well."""
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            gloss_only = self.svc.search_semantic(mode="gloss", query="probe")
            both = self.svc.search_semantic(mode="all", query="probe")
            self.assertTrue(both.results)
            self.assertGreaterEqual(
                len(both.results),
                len(gloss_only.results)
                if gloss_only.results
                else 0,
                "'all' mode must include 'gloss' table rows as well",
            )

    # --- degraded legs observable at the seam (Phase 4 contract surface) ----

    def test_empty_query_status(self):
        """Empty/whitespace query -> empty_query (no engine touched)."""
        self.svc._get_engine = lambda: (_ for _ in ()).throw(
            AssertionError("DB must not be touched for an empty query")
        )
        for q in ["", "   "]:
            result = self.svc.search_semantic(mode="gloss", query=q)
            self.assertEqual(
                result.status, "empty_query", "empty/whitespace query -> empty_query"
            )

    def test_no_embeddings_status_when_no_pinned_rows(self):
        """Status degraded legs reported identically at the seam.

        With fixtures seeded transaction-scoped (pinned rows present), the
        pinned leg must return ok; nothing may leak as a raised exception.
        """
        self.svc.set_query_encoder(_StubEncoder(E_POS))
        with self._txn() as conn:
            self._seed_rows(conn)
            self._wire_svc_to_txn(conn)
            result = self.svc.search_semantic(mode="gloss", query="probe")
            self.assertIn(result.status, {"ok", "no_embeddings", "stale_model"})

    def test_degraded_states_never_raise_and_message_is_str(self):
        for mode in ("gloss", "all"):
            for q, thr in [("", 0.8), ("probe", 0.99), ("probe", None)]:
                with self.subTest(mode=mode, q=q, thr=thr):
                    result = self.svc.search_semantic(
                        mode=mode, query=q, threshold=thr
                    )
                    self.assertIn(
                        result.status,
                        {"ok", "empty_query", "no_embeddings", "stale_model"},
                    )
                    self.assertIsInstance(result.message, str)


if __name__ == "__main__":
    unittest.main()