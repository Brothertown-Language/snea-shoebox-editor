# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-8 RED: FTS and Semantic strategies leave matched_terms as None.

The service ``search_records()`` in ``src/services/linguistic_service.py``
must return ``RecordSearchResult.matched_terms`` as ``None`` for FTS mode
and for Semantic Gloss / Semantic All modes whenever a search query is
present. Matched-term collection is an ILIKE-mode-only contract (SC-7);
the FTS and Semantic strategies must never fabricate a term map.

Fixture data lives in an isolated ephemeral PostgreSQL instance (pgserver) —
NEVER production data. The service is wired to the test DB by patching
``linguistic_service.get_session``. Semantic modes are exercised with the
seam strategy stubbed as a passthrough query transformer: the production
Records page dispatches Semantic Gloss / Semantic All through the #36 seam
directly (never through ``search_records``), and the real seam function
returns a ``SemanticSearchResult`` rather than a query transformer. The
stub isolates SC-8's contract — the ILIKE-only mode guard keeps
``matched_terms`` as None whenever a Semantic strategy is dispatched with
a query present — from that unrelated dispatch type mismatch.

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
    """SC-8 (behavioral): matched_terms stays None for FTS and Semantic modes."""

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
        from src.database.models.search import FTSEntry, SearchEntry
        from src.services.linguistic_service import LinguisticService

        norm = LinguisticService.generate_sort_lx

        session = orm.sessionmaker(bind=cls.engine)()
        source = Source(name="SC8 Seed Source")
        session.add(source)
        session.flush()
        cls.source_id = source.id

        # Record A: matches FTS query "cawap" via its FTS vector, and also
        # carries a Lexeme search entry. Its matched_terms must stay None
        # in FTS and Semantic modes.
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

        # Record B: FTS-vector-only record that also matches "wren", proving
        # the FTS path returns multiple records whose matched_terms stay None.
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

    # --- FTS mode ---

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
            "FTS mode must leave matched_terms as None (ILIKE-only collection)",
        )

    def test_fts_mode_none_across_multiple_records_sc8(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="wren", search_mode="FTS"
        )
        self.assertGreaterEqual(result.total_count, 1)
        self.assertIsNone(result.matched_terms)

    # --- Semantic modes ---

    def test_semantic_gloss_mode_leaves_matched_terms_none_sc8(self):
        from unittest.mock import patch

        from src.services.linguistic_service import LinguisticService

        # SC-8 contract under test: when a Semantic strategy is dispatched
        # with a query present, the ILIKE-only collection branch must not
        # fire — matched_terms stays None. The seam is stubbed as a
        # passthrough query transformer because the production page consumes
        # the real seam directly (SemanticSearchResult), never via
        # search_records; the stub isolates the mode-guard behavior. The
        # strategy dict binds the seam function at import time, so the dict
        # entry is patched, not the module attribute.
        passthrough = lambda query, search_term: query  # noqa: E731
        with patch.dict(
            "src.services.linguistic_service._search_strategies",
            {"Semantic Gloss": passthrough, "Semantic All": passthrough},
        ):
            result = LinguisticService.search_records(
                source_id=self.source_id,
                search_term="cawap",
                search_mode="Semantic Gloss",
            )
        self.assertGreater(
            result.total_count,
            0,
            "fixture must produce matches so the None assertion is meaningful",
        )
        self.assertIsNone(
            result.matched_terms,
            "Semantic Gloss mode must leave matched_terms as None",
        )

    def test_semantic_all_mode_leaves_matched_terms_none_sc8(self):
        from unittest.mock import patch

        from src.services.linguistic_service import LinguisticService

        passthrough = lambda query, search_term: query  # noqa: E731
        with patch.dict(
            "src.services.linguistic_service._search_strategies",
            {"Semantic All": passthrough},
        ):
            result = LinguisticService.search_records(
                source_id=self.source_id,
                search_term="wren",
                search_mode="Semantic All",
            )
        self.assertGreater(result.total_count, 0)
        self.assertIsNone(
            result.matched_terms,
            "Semantic All mode must leave matched_terms as None",
        )
