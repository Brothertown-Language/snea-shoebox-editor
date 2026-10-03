# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-7 RED: search_records() must collect matched raw terms.

The service ``search_records()`` in ``src/services/linguistic_service.py``
returns ``RecordSearchResult.matched_terms`` always as ``None``. This test
asserts the collection contract and FAILS before GREEN:

1. Per-mode collection: Lexeme, Headword, and Gloss (ILIKE) modes each collect
   the raw ``term`` values of the search entries that matched the query.
2. Per-record grouping: ``matched_terms`` is a mapping keyed by record
   identifier; only records whose entries matched are keyed.
3. Per-record dedup: repeated identical raw terms within one record collapse
   to a single entry; distinct raw matching terms are preserved.
4. Collection must be built from the existing paginated query (post-strategy
   dispatch), so only records on the returned page appear.

Fixture data lives in an isolated ephemeral PostgreSQL instance (pgserver) —
NEVER production data. The service is wired to the test DB by patching
``linguistic_service.get_session``.

Run: uv run pytest test/test_search_records_matched_terms_sc7_red.py

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import orm

from src.database.connection import get_db_url

TEST_PATH = Path("tmp/test_search_records_matched_terms_sc7_red_db")


def make_get_session(engine):
    @contextmanager
    def _get_session():
        session = orm.sessionmaker(bind=engine)()
        try:
            yield session
        finally:
            session.close()

    return _get_session


def _as_term_set(value):
    """Normalize a per-record term collection to a set without pinning the
    container type (set vs list is a GREEN implementation detail)."""
    return set(value)


class TestSearchRecordsMatchedTermsSc7Red(unittest.IsolatedAsyncioTestCase):
    """SC-7 (behavioral): matched raw-term collection in search_records()."""

    @classmethod
    def setUpClass(cls):  # noqa: N802
        try:
            import pgserver
            from sqlalchemy import create_engine

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

        from sqlalchemy import text

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
        from src.database.models.search import (
            GlossSearchEntry,
            HeadwordSearchEntry,
            SearchEntry,
        )
        from src.services.linguistic_service import LinguisticService

        norm = LinguisticService.generate_sort_lx

        session = orm.sessionmaker(bind=cls.engine)()
        source = Source(name="SC7 Seed Source")
        session.add(source)
        session.flush()

        cls.source_id = source.id

        # Record A: matches Lexeme "cawap" via two DISTINCT raw spellings,
        # plus a third duplicate row proving per-record dedup collapses it.
        rec_a = Record(lx="cawapou", source_id=source.id, mdf_data="")
        session.add(rec_a)
        session.flush()
        cls.rec_a_id = rec_a.id
        raw_terms_a = [("cawapou", "lx"), ("Cawapou", "lx"), ("cawapou", "se")]
        for raw, etype in raw_terms_a:
            session.add(
                SearchEntry(
                    record_id=rec_a.id,
                    term=raw,
                    normalized_term=norm(raw),
                    entry_type=etype,
                )
            )

        # Record B: headword entry matches "heki"; gloss entry does NOT,
        # so Gloss-mode search must NOT key record B.
        rec_b = Record(lx="heki", source_id=source.id, mdf_data="")
        session.add(rec_b)
        session.flush()
        cls.rec_b_id = rec_b.id
        session.add(
            HeadwordSearchEntry(
                record_id=rec_b.id, term="heki", normalized_term=norm("heki"), entry_type="lx"
            )
        )
        session.add(
            GlossSearchEntry(
                record_id=rec_b.id, term="wren", normalized_term=norm("wren"), entry_type="ge"
            )
        )

        # Record C: matches BOTH Headword and Gloss "heki"; gloss has a
        # duplicate raw term row proving per-record dedup in Gloss mode.
        rec_c = Record(lx="hekiuw", source_id=source.id, mdf_data="")
        session.add(rec_c)
        session.flush()
        cls.rec_c_id = rec_c.id
        session.add(
            HeadwordSearchEntry(
                record_id=rec_c.id, term="heki", normalized_term=norm("heki"), entry_type="va"
            )
        )
        for _ in range(2):
            session.add(
                GlossSearchEntry(
                    record_id=rec_c.id, term="heki", normalized_term=norm("heki"), entry_type="ge"
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

    def _keys(self, result):
        return {str(k) for k in result.matched_terms}

    # --- 1. Per-mode collection ---

    def test_lexeme_mode_collects_matched_raw_terms_sc7(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="cawap", search_mode="Lexeme"
        )
        self.assertIsNotNone(
            result.matched_terms,
            "Lexeme mode must populate matched_terms; currently always None",
        )
        self.assertEqual(self._keys(result), {str(self.rec_a_id)})
        self.assertEqual(_as_term_set(result.matched_terms[self.rec_a_id]), {"cawapou", "Cawapou"})

    def test_headword_mode_collects_matched_raw_terms_sc7(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="heki", search_mode="Headword"
        )
        self.assertIsNotNone(result.matched_terms)
        self.assertEqual(self._keys(result), {str(self.rec_b_id), str(self.rec_c_id)})
        self.assertEqual(_as_term_set(result.matched_terms[self.rec_b_id]), {"heki"})
        self.assertEqual(_as_term_set(result.matched_terms[self.rec_c_id]), {"heki"})

    def test_gloss_mode_collects_matched_raw_terms_sc7(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="heki", search_mode="Gloss"
        )
        self.assertIsNotNone(result.matched_terms)
        # Record B has a gloss but it does not match "heki" -> not keyed.
        self.assertEqual(self._keys(result), {str(self.rec_c_id)})
        self.assertEqual(_as_term_set(result.matched_terms[self.rec_c_id]), {"heki"})

    # --- 3. Per-record dedup ---

    def test_per_record_dedup_of_duplicate_raw_terms_sc7(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id, search_term="cawap", search_mode="Lexeme"
        )
        terms = _as_term_set(result.matched_terms[self.rec_a_id])
        # Three matching entry rows, two distinct raw spellings, one of them
        # duplicated -> dedup keeps exactly the distinct raw terms.
        self.assertEqual(terms, {"cawapou", "Cawapou"})
        self.assertEqual(len(terms), 2)

    # --- 4. Grouped to the paginated page only ---

    def test_matched_terms_grouping_follows_pagination_sc7(self):
        from src.services.linguistic_service import LinguisticService

        result = LinguisticService.search_records(
            source_id=self.source_id,
            search_term="heki",
            search_mode="Headword",
            limit=1,
        )
        self.assertEqual(len(result.records), 1)
        self.assertEqual(self._keys(result), {str(result.records[0]["id"])})
