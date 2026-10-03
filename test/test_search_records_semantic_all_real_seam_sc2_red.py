# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-2 RED (Issue #1404): Semantic All live path against the REAL seam.

``LinguisticService.search_records(search_mode='Semantic All',
search_term=...)`` must not raise and must return a ``RecordSearchResult``
whose ``matched_terms`` is populated from the seam's real per-record matched
terms (``SemanticSearchResult.matched_terms`` keyed by record id).

This test exercises the REAL ``search_semantic(mode='all')`` contract —
hits are the real ``(record_id, score)`` tuples UNION ALL'd across
``gloss_search_entries`` AND ``semantic_search_entries``, and matched terms
come from the real ``matched_terms`` dict — with ONLY the DB session
(``get_session``) and the query encoder patched. No ``_search_strategies``
shape stubs: the strategy dict keeps its real ``_search_semantic`` binding.

Pre-GREEN this must FAIL for the right reason: the strategy dispatch does
not thread ``mode='all'`` for ``'Semantic All'`` (only mode='gloss' is
threaded), so the real ``search_semantic('all')`` contract — including its
``semantic_search_entries`` UNION arm — is never exercised, and/or the
real tuple-hit shape is consumed as attribute-bearing hits
(``'tuple' object has no attribute 'record_id'``).

Fixture data lives in an isolated ephemeral PostgreSQL instance (pgserver) —
NEVER production data.

Run: uv run pytest test/test_search_records_semantic_all_real_seam_sc2_red.py

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import orm

TEST_PATH = Path("tmp/test_search_records_semantic_all_real_seam_sc2_red_db")

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


class TestSearchRecordsSemanticAllRealSeamSc2(unittest.TestCase):
    """SC-2: Semantic All mode works against the real search_semantic('all') seam."""

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
        from src.database.models.search import GlossSearchEntry, SemanticSearchEntry
        from src.services.semantic_search_service import PIN

        session = orm.sessionmaker(bind=cls.engine)()
        source = Source(name="SC2 Real Seam Seed Source")
        session.add(source)
        session.flush()
        cls.source_id = source.id

        # Record A: gloss_search_entries hit — embedded with the query vector
        # (cosine 1.0 clears the calibrated floor). Must surface via the
        # 'all' UNION's gloss arm.
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

        # Record C: semantic_search_entries hit — embedded with the query
        # vector (cosine 1.0 clears the floor). Must surface via the 'all'
        # UNION's semantic arm; this row ONLY exists in the semantic table,
        # so a dispatch that never threads mode='all' cannot return it.
        rec_c = Record(lx="skatook", source_id=source.id, mdf_data="")
        session.add(rec_c)
        session.flush()
        cls.rec_c_id = rec_c.id
        session.add(
            SemanticSearchEntry(
                record_id=rec_c.id,
                entry_type="lx",
                term="skatook",
                embedding=list(E_QUERY),
                embedding_model=PIN,
            )
        )

        # Record B: gloss embedded orthogonally — below the floor, must NOT
        # appear in the filtered result set.
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

        # Isolation: ONLY the DB session and the query encoder are patched.
        # The real search_semantic(mode='all') seam (real tuple hits, real
        # matched_terms dict) runs against the ephemeral fixture DB — no
        # _search_strategies shape stubs.
        self._session_patcher = patch.object(
            linguistic_service, "get_session", make_get_session(self.engine)
        )
        self._session_patcher.start()
        self.addCleanup(self._session_patcher.stop)

        # Point the seam's engine at the ephemeral fixture DB.
        self._engine_patcher = patch.object(svc, "_ENGINE", self.engine)
        self._engine_patcher.start()
        self.addCleanup(self._engine_patcher.stop)

        svc.set_query_encoder(_StubEncoder())
        self.addCleanup(svc.set_query_encoder, None)

    def test_semantic_all_real_seam_no_raise_and_matched_terms_sc2(self):
        from src.services.linguistic_service import LinguisticService
        from src.services.semantic_search_service import PIN

        result = LinguisticService.search_records(
            source_id=self.source_id,
            search_term="cawap",
            search_mode="Semantic All",
        )

        # SC-2: must not raise and must return a RecordSearchResult.
        self.assertIsNotNone(result)
        self.assertEqual(
            result.total_count,
            2,
            "both UNION arms must contribute: the gloss_search_entries hit "
            "AND the semantic_search_entries-only hit",
        )
        returned_ids = {rec["id"] for rec in result.records}
        self.assertEqual(
            returned_ids,
            {self.rec_a_id, self.rec_c_id},
            "the filtered result set must contain exactly the two "
            "floor-clearing semantic hits (gloss arm + semantic arm)",
        )
        self.assertNotIn(
            self.rec_b_id,
            returned_ids,
            "below-floor records must not appear in the result set",
        )

        # matched_terms must be populated from the seam's real per-record
        # matched terms dict (keyed by record id).
        self.assertIsNotNone(
            result.matched_terms,
            "Semantic All mode must populate matched_terms from the "
            "seam's real matched_terms dict",
        )
        self.assertIsInstance(result.matched_terms, dict)
        self.assertIn(self.rec_a_id, result.matched_terms)
        self.assertEqual(
            result.matched_terms[self.rec_a_id],
            {"cawapou"},
            "matched terms must carry the real gloss_search_entries term "
            f"seeded under pin {PIN}",
        )
        self.assertIn(self.rec_c_id, result.matched_terms)
        self.assertEqual(
            result.matched_terms[self.rec_c_id],
            {"skatook"},
            "matched terms must carry the real semantic_search_entries term "
            f"seeded under pin {PIN}",
        )
        self.assertNotIn(
            self.rec_b_id,
            result.matched_terms,
            "below-floor records must not contribute matched terms",
        )


if __name__ == "__main__":
    unittest.main()
