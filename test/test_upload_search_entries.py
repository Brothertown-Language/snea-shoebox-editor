import inspect
import unittest
from pathlib import Path

from src.database.connection import get_db_url
from src.services import embedding_service
from src.services import semantic_search_service as semantic_svc
from src.services.upload_service import UploadService


class TestUploadSearchEntriesRED(unittest.TestCase):
    """RED-phase tests for Phase 2: headword-block state for search entry population."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_upload_search_entries_red_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)

            with cls.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        from src.database.models.core import Language, Record, Source
        from src.database.models.identity import User
        from src.database.models.search import GlossSearchEntry, HeadwordSearchEntry, SearchEntry

        self.session = self.Session()
        self.session.query(GlossSearchEntry).delete()
        self.session.query(HeadwordSearchEntry).delete()
        self.session.query(SearchEntry).delete()
        self.session.query(Record).delete()

        if not self.session.query(User).filter_by(email="test@example.com").first():
            self.session.add(User(email="test@example.com", username="tester", github_id=1))
        if not self.session.query(Source).filter_by(name="Test Source").first():
            self.session.add(Source(name="Test Source"))
        if not self.session.query(Language).filter_by(code="alg").first():
            self.session.add(Language(code="alg", name="Algonquian"))
        self.session.commit()
        self.source_id = self.session.query(Source).filter_by(name="Test Source").first().id

    def tearDown(self):
        self.session.close()

    def _add_and_populate(self, mdf_data):
        from src.database.models.core import Record

        rec = Record(lx="entry", source_id=self.source_id, mdf_data=mdf_data)
        self.session.add(rec)
        self.session.commit()
        UploadService.populate_search_entries([rec.id], session=self.session)
        return rec

    # --- Item 2.1: HeadwordSearchEntry uses primary_va (SC-3) ---
    def test_headword_va_excludes_nested_va(self):
        """SC-3: HeadwordSearchEntry va must use primary_va, excluding nested va values."""
        from src.database.models.search import HeadwordSearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw"
            "\n"
            r"\va wampu-"
            "\n"
            r"\ge round object"
            "\n"
            r"\se wampuw-"
            "\n"
            r"  \va wampum"
        )
        entries = self.session.query(HeadwordSearchEntry).filter_by(record_id=rec.id).all()
        terms = [e.term for e in entries]
        self.assertIn("wampu-", terms, "Primary headword va should be in HeadwordSearchEntry")
        self.assertNotIn("wampum", terms, "Nested subentry va must NOT be in HeadwordSearchEntry")

    # --- Item 2.2: GlossSearchEntry uses in_headword_block state (SC-5, SC-23) ---
    def test_gloss_ge_excludes_nested_ge(self):
        """SC-5, SC-23: GlossSearchEntry ge must use headword-block ge, excluding nested ge values."""
        from src.database.models.search import GlossSearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw"
            "\n"
            r"\ge ball"
            "\n"
            r"\se wampuw-"
            "\n"
            r"  \ge sphere"
        )
        entries = self.session.query(GlossSearchEntry).filter_by(record_id=rec.id).all()
        terms = [e.term for e in entries]
        self.assertIn("ball", terms, "Primary headword ge should be in GlossSearchEntry")
        self.assertNotIn("sphere", terms, "Nested subentry ge must NOT be in GlossSearchEntry")

    # --- Item 2.3: Skip records missing \lx for HeadwordSearchEntry (SC-26) ---
    def test_no_lx_no_headword_entry(self):
        """SC-26: Record without lx must not create HeadwordSearchEntry."""
        from src.database.models.core import Record
        from src.database.models.search import HeadwordSearchEntry

        mdf_data = r"\ge orphan gloss" "\n" r"\ps n"
        rec = Record(lx="", source_id=self.source_id, mdf_data=mdf_data)
        self.session.add(rec)
        self.session.commit()
        UploadService.populate_search_entries([rec.id], session=self.session)
        count = self.session.query(HeadwordSearchEntry).filter_by(record_id=rec.id).count()
        self.assertEqual(count, 0, "Record without lx must not create HeadwordSearchEntry")

    # --- Item 2.4: SearchEntry population is unchanged (SC-4) ---
    def test_search_entry_unchanged(self):
        """SC-4: SearchEntry must still contain ALL values including nested ones."""
        from src.database.models.search import SearchEntry

        rec = self._add_and_populate(
            r"\lx wampuw"
            "\n"
            r"\va wampu-"
            "\n"
            r"\ge round"
            "\n"
            r"\se wampuw-"
            "\n"
            r"\cf wampuch"
            "\n"
            r"\ve fire"
        )
        entries = self.session.query(SearchEntry).filter_by(record_id=rec.id).all()
        types = sorted([e.entry_type for e in entries])
        self.assertEqual(types, ["cf", "lx", "se", "va", "ve"], "SearchEntry must contain ALL entry types (unchanged)")


# --- Item 8 (SC-8, behavioral) — inline embedding during ingestion ----------


class TestUploadSearchEntriesEmbeddingSC8(unittest.TestCase):
    """SC-8 (behavioral): populate_search_entries embeds new primary ge rows
    inline during ingestion against the freshly synced local DB — signature
    unchanged, embedding IS NOT NULL, embedding_model == current pin, real
    Algonquian Unicode preserved exactly, and every DB write batch ≤ 512.

    Fixture records are transaction-scoped copies of REAL synced records
    (mdf_data copied verbatim from records by id); the outer transaction rolls
    back so the synced dataset is untouched.

    Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
    """

    # REAL synced record ids (verified live on the synced local DB):
    #   5    lx='ayhkôsu-'      ge='he works'
    #   15   lx='-côq'          ge='DEP soul, spirit of a living person …'
    #   6832 lx='|nashqunánum|' ge='(with |nꝏtau|) `he kindles' (a fire)'  (ꝏ is the remediated oo-ligature, #1411)
    REAL_RECORD_IDS = [5, 15, 6832]

    @classmethod
    def setUpClass(cls):  # noqa: N802
        import psycopg2

        try:
            psycopg2.connect(host="localhost", port=5432, dbname="postgres", user="postgres").close()
        except Exception:
            raise unittest.SkipTest("synced local DB not reachable") from None
        from sqlalchemy import create_engine, text  # noqa: F401
        from sqlalchemy import text as sa_text

        cls.engine = create_engine(get_db_url())
        # Stashed in a tuple: a bare class-attribute function would bind into
        # a bound method when read back through `self.` (descriptor protocol).
        cls.sa_text = (sa_text,)
        cls.batch_sizes = []

    def setUp(self):
        from sqlalchemy.orm import Session

        from src.database.models.search import FTSEntry, GlossSearchEntry, HeadwordSearchEntry, SearchEntry
        from src.services import upload_service as usvc

        self.usvc = usvc
        self.batch_sizes = []
        self._real_encode = embedding_service.encode
        self._real_get_session = usvc.get_session
        # Note: upload_service imports populate_search_entries' ge population
        # path calls embedding_service at module level — RED asserts encode()
        # IS invoked here once inline embedding lands (GREEN, Item 9).

        # Outer transaction; every mutation (including populate's own
        # session.commit()) stays uncommitted and is rolled back on exit.
        self.conn = self.engine.connect()
        self.txn = self.conn.begin()
        self.session = Session(bind=self.conn, join_transaction_mode="create_savepoint")
        usvc.get_session = lambda: self.session

        # Wrap the real encoder to record DB-write batch sizes (assert ≤512),
        # delegating to the real pinned model so embeddings are genuine.
        def _recording_encode(texts):
            texts = [texts] if isinstance(texts, str) else list(texts)
            self.batch_sizes.append(len(texts))
            return self._real_encode(texts)

        self._recording_encode = _recording_encode
        embedding_service.encode = _recording_encode
        self._search_models = (SearchEntry, HeadwordSearchEntry, GlossSearchEntry, FTSEntry)

    def tearDown(self):
        self.session.close()
        self.txn.rollback()
        self.conn.close()
        embedding_service.encode = self._real_encode
        self.usvc.get_session = self._real_get_session

    def _fixture_records(self):
        """Insert transaction-scoped Record copies of REAL synced records and
        return (record_ids, expected_ge_terms) from the synced DB verbatim."""
        from src.database.models.core import Record

        fetched = []
        with self.engine.connect() as probe:
            for rid in self.REAL_RECORD_IDS:
                row = probe.execute(
                    self.sa_text[0]("SELECT id, mdf_data FROM records WHERE id = :rid AND is_deleted = false"),
                    {"rid": rid},
                ).fetchone()
                self.assertIsNotNone(row, f"real synced record {rid} must exist in synced DB")
                fetched.append(row)
        # Create fixture Record copies in REAL_RECORD_IDS order and capture
        # the real→new id mapping from the freshly added objects themselves.
        new_records = []
        source_id = self.session.query(Record.source_id).limit(1).scalar() or 1
        for _rid, mdf in fetched:
            rec = Record(lx="", source_id=source_id, mdf_data=mdf)
            self.session.add(rec)
            new_records.append(rec)
        self.session.flush()
        new_ids = [r.id for r in new_records]
        real_ge = {}
        with self.engine.connect() as probe:
            for rid in self.REAL_RECORD_IDS:
                ge = probe.execute(self.sa_text[0]("SELECT ge FROM records WHERE id = :rid"), {"rid": rid}).scalar()
                real_ge[rid] = ge
        return new_ids, [real_ge[rid] for rid in self.REAL_RECORD_IDS]

    def test_sc8_signature_unchanged_returns_int(self):
        """SC-8: signature is populate_search_entries(record_ids, session=None)
        → int (unchanged)."""
        sig = inspect.signature(self.usvc.UploadService.populate_search_entries)
        params = list(sig.parameters)
        self.assertEqual(params, ["record_ids", "session"], "signature unchanged")
        self.assertIsInstance(
            sig.parameters["session"].default,
            type(None),
            "session param default stays None",
        )

    def test_sc8_ge_rows_embedded_with_pin(self):
        """SC-8: ingested ge rows carry embedding IS NOT NULL and
        embedding_model == the current pin (thenlper/gte-small)."""
        record_ids, _ = self._fixture_records()
        result = self.usvc.UploadService.populate_search_entries(record_ids)  # session=None
        self.assertIsInstance(result, int, "returns int")
        from src.database.models.search import GlossSearchEntry

        rows = (
            self.session.query(GlossSearchEntry)
            .filter(GlossSearchEntry.record_id.in_(record_ids))
            .filter(GlossSearchEntry.entry_type == "ge")
            .all()
        )
        self.assertTrue(rows, "ge rows must be populated")
        for row in rows:
            self.assertIsNotNone(row.embedding, "embedding IS NOT NULL on ingested ge row")
            self.assertEqual(
                row.embedding_model,
                semantic_svc.PIN,
                "embedding_model stamped with the current pin",
            )
            self.assertEqual(len(row.embedding), 384, "pgvector dimension 384")

    def test_sc8_unicode_preserved_exactly_on_real_records(self):
        """SC-8: Unicode preserved exactly — gloss term round-trips verbatim
        from real synced records (ô, á, ꝏ etc.).

        The expected term is parsed from the synced record's mdf_data with
        parse_mdf — the same source of truth the ingestion pipeline uses —
        not from the denormalized records.ge column, which can lag behind
        mdf_data remediation (#1421)."""
        from src.mdf.parser import parse_mdf

        record_ids, _ = self._fixture_records()
        self.usvc.UploadService.populate_search_entries(record_ids)
        from src.database.models.search import GlossSearchEntry

        real_ge_by_id = {}
        with self.engine.connect() as probe:
            for rid in self.REAL_RECORD_IDS:
                mdf = probe.execute(
                    self.sa_text[0]("SELECT mdf_data FROM records WHERE id = :rid"), {"rid": rid}
                ).scalar()
                parsed = parse_mdf(mdf)
                real_ge_by_id[rid] = parsed[0].get("ge", "") if parsed else ""
        new_to_real = dict(zip(record_ids, self.REAL_RECORD_IDS, strict=False))
        rows = self.session.query(GlossSearchEntry).filter(GlossSearchEntry.record_id.in_(record_ids)).all()
        by_record = {}
        for row in rows:
            by_record.setdefault(row.record_id, []).append(row.term)
        for new_id in record_ids:
            expected = real_ge_by_id[new_to_real[new_id]]
            if not expected:
                continue
            self.assertIn(
                expected,
                by_record.get(new_id, []),
                "Unicode preserved exactly (term round-trips verbatim from synced record)",
            )

    def test_sc8_batch_writes_le_512(self):
        """SC-8: every encode/DB write batch ≤ 512 strings."""
        record_ids, _ = self._fixture_records()
        self.usvc.UploadService.populate_search_entries(record_ids)
        self.assertTrue(
            self.batch_sizes,
            "embedding_service.encode must be invoked inline during ingestion",
        )
        for size in self.batch_sizes:
            self.assertLessEqual(size, 512, "batch ≤ 512 on writes")


if __name__ == "__main__":
    unittest.main()
