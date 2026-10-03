# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-8 RED (revised 2026-10-03): FTS keeps matched_terms None; Semantic modes populate it.

The service ``search_records()`` in ``src/services/linguistic_service.py``
must return ``RecordSearchResult.matched_terms`` as ``None`` for FTS mode,
and must POPULATE ``matched_terms`` for Semantic Gloss / Semantic All modes
from the matched source-field term values carried by the semantic search
layer's ``SemanticSearchResult`` hits — grouped per record identifier and
deduplicated per record.

Fixture data lives in an isolated ephemeral PostgreSQL instance (pgserver) —
NEVER production data. The service is wired to the test DB by patching
``linguistic_service.get_session``. The fixture seeds ``SemanticSearchEntry``
rows with embeddings (pinned model) so the semantic layer's data model is
present. Semantic modes are exercised with the strategy dispatch stubbed as
a passthrough returning ``SemanticSearchResult`` hit instances (carrying
``record_id``, ``entry_type``, ``term``, ``similarity``) instead of running
the real embedding seam — the same isolation pattern the existing SC-8
semantic cases use; the stub isolates SC-8's matched-terms population
contract from the real vector-encoding path.

Pre-GREEN the Semantic cases must FAIL: ``matched_terms`` is currently None
for semantic modes (ILIKE-only collection branch).

Run: uv run pytest test/test_search_records_matched_terms_none_sc8_red.py

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import func, orm

TEST_PATH = Path("tmp/test_search_records_matched_terms_none_sc8_red_db")


def make_get_session(engine):
    @contextmanager
    def _get_session():
        session = orm.sessionmaker(bind=engine)()
        try:
            yield session
        finally:
            session.close()

    return _get_session


class TestSearchRecordsMatchedTermsNoneSc8(unittest.TestCase):
    """SC-8: FTS matched_terms None; Semantic modes populate per-record terms."""

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
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if TEST_PATH.exists():
            shutil.rmtree(TEST_PATH, ignore_errors=True)

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.search import FTSEntry, SearchEntry, SemanticSearchEntry
        from src.services.linguistic_service import LinguisticService
        from src.services.semantic_search_service import PIN

        norm = LinguisticService.generate_sort_lx

        session = orm.sessionmaker(bind=cls.engine)()
        source = Source(name="SC8 Seed Source")
        session.add(source)
        session.flush()
        cls.source_id = source.id

        # Record A: matches FTS query "cawap" via its FTS vector, carries a
        # Lexeme search entry, and a semantic entry ("cawapou") with an
        # embedding under the pinned model. matched_terms: None in FTS mode;
        # populated from the semantic layer's source-field terms in Semantic
        # modes.
        rec_a = Record(lx="cawapou", source_id=source.id, mdf_data="")
        session.add(rec_a)
        session.flush()
        cls.rec_a_id = rec_a.id
        session.add(
            SearchEntry(
                record_id=rec_a.id,
                term="cawapou",
                normalized_term=norm("cawapou"),
                entry_type="lx",
            )
        )
        session.add(
            FTSEntry(
                record_id=rec_a.id,
                fts_vector=func.to_tsvector("simple", norm("cawapou cawapou wren")),
            )
        )
        session.add(
            SemanticSearchEntry(
                record_id=rec_a.id,
                entry_type="lx",
                term="cawapou",
                embedding=[0.1] * 384,
                embedding_model=PIN,
            )
        )

        # Record B: FTS-vector-only record that also matches "wren", plus a
        # semantic entry ("wrenuw") — proves multi-record semantic population.
        rec_b = Record(lx="wrenuw", source_id=source.id, mdf_data="")
        session.add(rec_b)
        session.flush()
        cls.rec_b_id = rec_b.id
        session.add(
            FTSEntry(
                record_id=rec_b.id,
                fts_vector=func.to_tsvector("simple", norm("wren heki")),
            )
        )
        session.add(
            SemanticSearchEntry(
                record_id=rec_b.id,
                entry_type="va",
                term="wrenuw",
                embedding=[0.2] * 384,
                embedding_model=PIN,
            )
        )

        session.commit()
        session.close()

    def setUp(self):
        from unittest.mock import patch

        from src.services import linguistic_service

        self._patcher = patch.object(
            linguistic_service, "get_session", make_get_session(self.engine)
        )
        self._patcher.start()
        self.addCleanup(self._patcher.stop)

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

    def test_fts_mode_none_across_multiple_records_sc8(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="wren", search_mode="FTS"
        )
        self.assertGreaterEqual(result.total_count, 1)
        self.assertIsNone(result.matched_terms)

    # --- Semantic modes: matched_terms populated from the semantic layer ---

    @staticmethod
    def _make_semantic_stub(hits):
        """Strategy stub returning SemanticSearchResult hit instances.

        Isolation pattern: the strategy dict binds the seam function at
        import time, so the dict entry is patched (not the module attribute).
        The stub returns the semantic search layer's per-hit objects — each
        carrying (record_id, entry_type, term, similarity) — instead of
        running the real vector-encoding seam.
        """
        from src.database.models.search import SemanticSearchResult

        def _stub(query, search_term):
            return [
                SemanticSearchResult(
                    record_id=hit.record_id,
                    entry_type=hit.entry_type,
                    term=hit.term,
                    similarity=hit.similarity,
                )
                for hit in hits
            ]

        return _stub

    def test_semantic_gloss_populates_matched_terms_dedup_sc8(self):
        from unittest.mock import patch

        from src.services import linguistic_service

        # Record A matched with the same term carried under two entry types
        # plus a second distinct source-field term — the per-record set must
        # be deduplicated to {"cawapou", "cawap"}.
        from src.database.models.search import SemanticSearchResult

        hits = [
            SemanticSearchResult(
                record_id=self.rec_a_id, entry_type="lx", term="cawapou", similarity=0.97
            ),
            SemanticSearchResult(
                record_id=self.rec_a_id, entry_type="ge", term="cawapou", similarity=0.96
            ),
            SemanticSearchResult(
                record_id=self.rec_a_id, entry_type="ge", term="cawap", similarity=0.95
            ),
        ]
        stub = self._make_semantic_stub(hits)
        with patch.dict(
            "src.services.linguistic_service._search_strategies",
            {"Semantic Gloss": stub},
        ):
            result = linguistic_service.LinguisticService.search_records(
                source_id=self.source_id,
                search_term="cawap",
                search_mode="Semantic Gloss",
            )
        self.assertGreater(
            result.total_count,
            0,
            "fixture must produce semantic matches so the presence assertion is meaningful",
        )
        self.assertIsNotNone(
            result.matched_terms,
            "Semantic Gloss mode must populate matched_terms from the "
            "matched source-field terms",
        )
        self.assertIsInstance(result.matched_terms, dict)
        self.assertIn(
            self.rec_a_id,
            result.matched_terms,
            "matched_terms must be keyed by record id",
        )
        self.assertEqual(
            result.matched_terms[self.rec_a_id],
            {"cawapou", "cawap"},
            "matched_terms per record must be the deduplicated set of "
            "matched source-field terms",
        )

    def test_semantic_all_populates_matched_terms_multiple_records_sc8(self):
        from unittest.mock import patch

        from src.database.models.search import SemanticSearchResult
        from src.services import linguistic_service

        hits = [
            SemanticSearchResult(
                record_id=self.rec_a_id, entry_type="lx", term="cawapou", similarity=0.97
            ),
            SemanticSearchResult(
                record_id=self.rec_a_id, entry_type="ge", term="cawapou", similarity=0.96
            ),
            SemanticSearchResult(
                record_id=self.rec_b_id, entry_type="va", term="wrenuw", similarity=0.94
            ),
            SemanticSearchResult(
                record_id=self.rec_b_id, entry_type="ge", term="wrenuw", similarity=0.93
            ),
        ]
        stub = self._make_semantic_stub(hits)
        with patch.dict(
            "src.services.linguistic_service._search_strategies",
            {"Semantic All": stub},
        ):
            result = linguistic_service.LinguisticService.search_records(
                source_id=self.source_id,
                search_term="wren",
                search_mode="Semantic All",
            )
        self.assertGreaterEqual(result.total_count, 2)
        self.assertIsNotNone(
            result.matched_terms,
            "Semantic All mode must populate matched_terms from the "
            "matched source-field terms",
        )
        self.assertIn(self.rec_a_id, result.matched_terms)
        self.assertIn(self.rec_b_id, result.matched_terms)
        self.assertEqual(
            result.matched_terms[self.rec_a_id],
            {"cawapou"},
            "duplicate source-field terms must deduplicate per record",
        )
        self.assertEqual(
            result.matched_terms[self.rec_b_id],
            {"wrenuw"},
            "duplicate source-field terms must deduplicate per record",
        )


if __name__ == "__main__":
    unittest.main()
