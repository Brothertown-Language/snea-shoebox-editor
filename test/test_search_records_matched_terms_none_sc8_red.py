# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-3 (Issue #1404): REAL search_semantic hit shapes — contract-enforcement suite.

``LinguisticService.search_records()`` must consume the REAL ``search_semantic``
contract for both Semantic modes:

- the container shape: ``SemanticSearchResult`` whose ``results`` is a list of
  ``(record_id, score)`` tuples and whose ``matched_terms`` is a real
  ``dict[int, set]`` keyed by record id — NOT attribute-bearing hit stubs;
- the ``(record_id, score)`` tuple hit shape exactly as the seam returns it
  (``src/services/semantic_search_service.py::search_semantic`` appends
  ``(int(record_id), float(score))`` per row).

This suite is a CONTRACT-ENFORCEMENT suite, not a shape-stub suite:

- ONLY the DB session (``linguistic_service.get_session``), the seam's engine
  (``semantic_search_service._ENGINE``), and the query encoder
  (``set_query_encoder``) are patched. The real ``search_semantic`` seam runs
  against an ephemeral pgserver fixture DB and returns its genuine tuple hits
  and ``matched_terms`` dict.
- A guard test greps THIS module's source for ``_search_strategies`` patching
  and FAILS if any shape stub remains. The guard passes post-rewrite by
  design: its purpose is to lock the contract in — any later reintroduction
  of ``_search_strategies`` stubbing in this file turns the suite RED.

FTS cases are retained (matched_terms stays None — unchanged contract).

Fixture data lives in an isolated ephemeral PostgreSQL instance (pgserver) —
NEVER production data.

Run: uv run pytest test/test_search_records_matched_terms_none_sc8_red.py

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import func, orm

TEST_PATH = Path("tmp/test_search_records_matched_terms_none_sc8_red_db")

# Pinned-model dimension (gte-small).
DIM = 384
# Deterministic query vector; matched rows embed this exact vector so the
# cosine similarity is 1.0 — above the CALIBRATED_FLOOR default (0.93).
E_QUERY = [0.1] * DIM
# Orthogonal vector for a non-matching row (cosine ~0 < floor).
E_FAR = [0.0] * DIM
E_FAR[0] = 1.0


class _StubEncoder:
    """Deterministic encoder: every query maps to E_QUERY."""

    def encode(self, texts):
        return [list(E_QUERY) for _ in texts]


def make_get_session(engine):
    @contextmanager
    def _get_session():
        session = orm.sessionmaker(bind=engine)()
        try:
            yield session
        finally:
            session.close()

    return _get_session


class TestSearchRecordsRealSemanticShapesSc3(unittest.TestCase):
    """SC-3: real search_semantic shapes for both modes; no shape stubs."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        try:
            import pgserver
            from sqlalchemy import create_engine, text

            from src.database.base import Base

            # Import model modules so their tables register on Base.metadata
            # before create_all.
            import src.database.models.core  # noqa: F401, PLC0415
            import src.database.models.identity  # noqa: F401, PLC0415
            import src.database.models.search  # noqa: F401, PLC0415
            import src.database.models.workflow  # noqa: F401, PLC0415
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

        if TEST_PATH.exists():
            shutil.rmtree(TEST_PATH)
        TEST_PATH.mkdir(parents=True, exist_ok=True)
        cls._test_path = TEST_PATH

        cls.pg_server = pgserver.get_server(str(TEST_PATH))
        cls.db_url = cls.pg_server.get_uri()
        cls.engine = create_engine(cls.db_url)

        with cls.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        Base.metadata.create_all(cls.engine)
        cls._seed()

    @classmethod
    def tearDownClass(cls):  # noqa: N802
        from src.services import semantic_search_service as svc

        svc.set_query_encoder(None)
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if TEST_PATH.exists():
            shutil.rmtree(TEST_PATH, ignore_errors=True)

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.search import FTSEntry, GlossSearchEntry
        from src.database.models.search import SemanticSearchEntry
        from src.services.semantic_search_service import PIN

        session = orm.sessionmaker(bind=cls.engine)()
        source = Source(name="SC3 Real Shape Seed Source")
        session.add(source)
        session.flush()
        cls.source_id = source.id

        # Record A: primary gloss embedded with the query vector (cosine 1.0
        # clears the calibrated floor) — gloss seam hit. Also carries a
        # semantic entry under the same pinned model — Semantic All (gloss ∪
        # semantic union) hit. FTS vector present for the FTS None cases.
        rec_a = Record(lx="cawapou", source_id=source.id, mdf_data="")
        session.add(rec_a)
        session.flush()
        cls.rec_a_id = rec_a.id
        session.add(
            GlossSearchEntry(
                record_id=rec_a.id,
                entry_type="ge",
                term="cawapou",
                normalized_term="cawapou",
                embedding=list(E_QUERY),
                embedding_model=PIN,
            )
        )
        session.add(
            SemanticSearchEntry(
                record_id=rec_a.id,
                entry_type="va",
                term="cawap",
                embedding=list(E_QUERY),
                embedding_model=PIN,
            )
        )
        session.add(
            FTSEntry(
                record_id=rec_a.id,
                fts_vector=func.to_tsvector("simple", "cawapou cawapou wren"),
            )
        )

        # Record B: below-floor gloss — must NOT surface as a semantic hit.
        rec_b = Record(lx="wrenuw", source_id=source.id, mdf_data="")
        session.add(rec_b)
        session.flush()
        cls.rec_b_id = rec_b.id
        session.add(
            GlossSearchEntry(
                record_id=rec_b.id,
                entry_type="ge",
                term="wren",
                normalized_term="wren",
                embedding=list(E_FAR),
                embedding_model=PIN,
            )
        )

        session.commit()
        session.close()

    def setUp(self):
        from src.services import linguistic_service
        from src.services import semantic_search_service as svc

        # Isolation: ONLY the DB session, the seam engine, and the query
        # encoder are patched. The real search_semantic seam (real
        # (record_id, score) tuple hits, real matched_terms dict) runs
        # against the ephemeral fixture DB. NO _search_strategies stubs.
        self._session_patcher = patch.object(
            linguistic_service, "get_session", make_get_session(self.engine)
        )
        self._session_patcher.start()
        self.addCleanup(self._session_patcher.stop)

        self._engine_patcher = patch.object(svc, "_ENGINE", self.engine)
        self._engine_patcher.start()
        self.addCleanup(self._engine_patcher.stop)

        svc.set_query_encoder(_StubEncoder())
        self.addCleanup(svc.set_query_encoder, None)

    # --- SC-3 contract guard: no _search_strategies shape stubs ---

    def test_no_search_strategies_shape_stubs_in_module_sc3(self):
        """Guard: this module must not stub the _search_strategies table.

        Post-rewrite this guard PASSES by design — it locks the contract
        in. The SC-3 suite FAILS only if a shape stub is reintroduced here
        (or the real contract assertions below stop being exercised).
        """
        import re

        source = Path(__file__).read_text(encoding="utf-8")
        # Detect actual stub *patching* patterns — any patch.dict /
        # patch.object call targeting the strategy table (regardless of
        # import aliasing), or direct table access/assignment.
        stub_pattern = re.compile(
            r"\.(?:dict|object)\(\s*[\"'][^\"']*_search_strategies"
            r"|_search_strategies\s*[\[{=]"
        )
        self.assertIsNone(
            stub_pattern.search(source),
            "SC-3 contract violation: this suite must exercise the real "
            "search_semantic seam, never stub _search_strategies hit shapes",
        )

    # --- SC-3: Semantic Gloss — real container + (record_id, score) tuples ---

    def test_semantic_gloss_real_container_tuple_hits_sc3(self):
        from src.services.linguistic_service import LinguisticService
        from src.services.semantic_search_service import search_semantic

        # Verify the real seam itself returns the genuine contract shapes:
        # a SemanticSearchResult container whose results are
        # (record_id, score) tuples and whose matched_terms is a real dict.
        container = search_semantic(mode="gloss", query="cawap")
        self.assertIsNotNone(container.results)
        self.assertTrue(
            all(
                isinstance(hit, tuple) and len(hit) == 2
                for hit in container.results
            ),
            "the real seam must return (record_id, score) tuple hits — "
            "attribute-bearing hit objects would mean the seam contract "
            "changed and this suite no longer exercises SC-3's shapes",
        )
        self.assertIsInstance(
            container.matched_terms,
            dict,
            "the real seam must populate matched_terms as a dict keyed "
            "by record id",
        )

        # Now through the service: the real tuple hits must be consumed
        # without raising, and matched_terms must flow from the seam's
        # real dict.
        result = LinguisticService.search_records(
            source_id=self.source_id,
            search_term="cawap",
            search_mode="Semantic Gloss",
        )
        self.assertEqual(
            result.total_count,
            1,
            "exactly the floor-clearing record must be returned",
        )
        returned_ids = {rec["id"] for rec in result.records}
        self.assertEqual(
            returned_ids,
            {self.rec_a_id},
            "the filtered result set must contain exactly the semantic "
            "hit record",
        )
        self.assertIsNotNone(
            result.matched_terms,
            "Semantic Gloss mode must populate matched_terms from the "
            "seam's real matched_terms dict",
        )
        self.assertIn(self.rec_a_id, result.matched_terms)
        self.assertEqual(
            result.matched_terms[self.rec_a_id],
            {"cawapou"},
            "matched terms must carry the real gloss_search_entries term",
        )
        self.assertNotIn(
            self.rec_b_id,
            result.matched_terms,
            "below-floor records must not contribute matched terms",
        )

    # --- SC-3: Semantic All — real container + (record_id, score) tuples ---

    def test_semantic_all_real_container_tuple_hits_sc3(self):
        from src.services.linguistic_service import LinguisticService
        from src.services.semantic_search_service import search_semantic

        # Real 'all' seam: gloss ∪ semantic union, same tuple contract.
        container = search_semantic(mode="all", query="cawap")
        self.assertTrue(
            all(
                isinstance(hit, tuple) and len(hit) == 2
                for hit in container.results
            ),
            "the real seam must return (record_id, score) tuple hits in "
            "'all' mode as well",
        )
        self.assertIsInstance(container.matched_terms, dict)

        result = LinguisticService.search_records(
            source_id=self.source_id,
            search_term="cawap",
            search_mode="Semantic All",
        )
        self.assertEqual(
            result.total_count,
            1,
            "exactly the floor-clearing record must be returned in 'all' mode",
        )
        returned_ids = {rec["id"] for rec in result.records}
        self.assertEqual(returned_ids, {self.rec_a_id})
        self.assertIsNotNone(
            result.matched_terms,
            "Semantic All mode must populate matched_terms from the "
            "seam's real matched_terms dict",
        )
        # 'all' unions gloss and semantic tables: both seeded terms for
        # record A must appear, deduplicated per record.
        self.assertEqual(
            result.matched_terms[self.rec_a_id],
            {"cawapou", "cawap"},
            "Semantic All matched_terms must union gloss and semantic "
            "table terms, deduplicated per record",
        )

    # --- FTS mode: matched_terms stays None (unchanged contract) ---

    def test_fts_mode_leaves_matched_terms_none_sc8(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="cawap", search_mode="FTS"
        )
        self.assertGreater(
            result.total_count,
            0,
            "fixture must produce FTS matches so the None assertion is meaningful",
        )
        self.assertIsNone(
            result.matched_terms,
            "FTS mode must leave matched_terms as None (no raw-term anchor)",
        )


if __name__ == "__main__":
    unittest.main()
