import unittest
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.models.core import Language, Record, RecordLanguage, Source
from src.database.models.identity import User
from src.database.models.workflow import MatchupQueue
from src.services.upload_service import UploadService


class TestLanguageAssignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pgserver

            cls.test_db_path = Path("tmp/test_lang_assignment_db")
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

            # Seed ISO 639-3 data required for language validation
            import csv
            from pathlib import Path as _Path

            from src.database.models.iso639 import ISO639_3

            _data_file = _Path("src/database/data/iso-639-3.tab")
            _Session = sessionmaker(bind=cls.engine)
            _sess = _Session()
            if _sess.query(ISO639_3).count() == 0:
                with open(_data_file, encoding="utf-8") as _f:
                    _reader = csv.DictReader(_f, delimiter="\t")
                    _sess.add_all(
                        [
                            ISO639_3(
                                id=r["Id"],
                                part2b=r.get("Part2b") or None,
                                part2t=r.get("Part2t") or None,
                                part1=r.get("Part1") or None,
                                scope=r["Scope"],
                                language_type=r["Language_Type"],
                                ref_name=r["Ref_Name"],
                                comment=r.get("Comment") or None,
                            )
                            for r in _reader
                        ]
                    )
                    _sess.commit()
            _sess.close()
        except ImportError as err:
            raise unittest.SkipTest("pgserver not installed") from err

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def setUp(self):
        self.session = self.Session()
        # Clean up tables
        with self.engine.connect() as conn:
            conn.execute(
                text(
                    "TRUNCATE user_activity_log, record_languages, edit_history, "
                    "search_entries, records, languages, matchup_queue, users, sources "
                    "RESTART IDENTITY CASCADE;"
                )
            )
            conn.commit()

        # Create a user
        self.user = User(email="test@example.com", username="testuser", github_id=123)
        self.session.add(self.user)
        self.session.commit()

        # Create a source
        self.source = Source(name="Test Source")
        self.session.add(self.source)
        self.session.flush()
        self.source_id = self.source.id

    def tearDown(self):
        self.session.close()

    def _commit_mdf(self, lx, mdf_data):
        batch_id = str(uuid.uuid4())
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx=lx,
            mdf_data=mdf_data,
        )
        self.session.add(q_row)
        self.session.commit()

        from unittest.mock import patch

        with (
            patch("src.services.upload_service.get_session", return_value=self.session),
            patch("src.services.audit_service.get_session", return_value=self.session),
        ):
            UploadService.commit_new(batch_id, "test@example.com", str(uuid.uuid4()))

        return self.session.query(Record).filter_by(lx=lx).first()

    def test_scenario_1_headword_so_only(self):
        r"""1) headword has \so, sub entries do not = record has a primary language"""
        mdf_data = "\\lx test1\n\\so Mohegan-Pequot [xpq]\n\\ge test gloss\n\\se subentry\n\\ge subgloss"
        record = self._commit_mdf("test1", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        self.assertTrue(record_langs[0].is_primary)

        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "xpq")

    def test_scenario_2_headword_and_subentry_so(self):
        r"""2) headword has \so, subentries have \so = record has both a primary language and secondary languages"""
        mdf_data = (
            "\\lx test2\n\\so Mohegan-Pequot [xpq]\n\\ge test gloss\n\\se subentry\n\\so English [eng]\n\\ge subgloss"
        )
        record = self._commit_mdf("test2", mdf_data)

        record_langs = (
            self.session.query(RecordLanguage).filter_by(record_id=record.id).order_by(RecordLanguage.id).all()
        )
        self.assertEqual(len(record_langs), 2)

        # Primary
        self.assertTrue(record_langs[0].is_primary)
        lang1 = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang1.code, "xpq")

        # Secondary
        self.assertFalse(record_langs[1].is_primary)
        lang2 = self.session.get(Language, record_langs[1].language_id)
        self.assertEqual(lang2.code, "eng")

    def test_scenario_3_subentry_so_only(self):
        r"""3) headwords without \so, subentries with \so = no primary, secondary languages only"""
        mdf_data = "\\lx test3\n\\ge test gloss\n\\se subentry\n\\so Mohegan-Pequot [xpq]\n\\ge subgloss"
        record = self._commit_mdf("test3", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        self.assertFalse(record_langs[0].is_primary)

        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "xpq")

    def test_scenario_4_no_so(self):
        r"""4) headwords does not have \so, subentries do not have \so = records does not have any languages"""
        mdf_data = "\\lx test4\n\\ge test gloss\n\\se subentry\n\\ge subgloss"
        record = self._commit_mdf("test4", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 0)


# ── RED-phase tests for ISO 639-3 language identification (issue #1339) ──

    def test_mohican_mjy_creates_correct_language(self):
        r"""SC-1 (MUST FAIL currently): Mohican [mjy] creates Language(code=mjy, name="Mahican").

        Currently fails because "Mohican != Mahican" hits the ref_name != lg_name guard.
        After fix, JaroWinkler("Mohican", "Mahican") >= 0.75 passes and the Language is created.
        """
        mdf_data = "\\lx mohican_test\n\\so Mohican [mjy]\n\\ge test gloss"
        record = self._commit_mdf("mohican_test", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)

        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "mjy")
        self.assertEqual(lang.name, "Mahican")

    def test_english_eng_still_works(self):
        r"""SC-2 (MUST PASS currently): English [eng] still creates RecordLanguage.

        Regression guard — "English == English" passes the guard today and must
        continue to work after the fix.
        """
        mdf_data = "\\lx english_test\n\\so English [eng]\n\\ge test gloss"
        record = self._commit_mdf("english_test", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)

        lang = self.session.get(Language, record_langs[0].language_id)
        self.assertEqual(lang.code, "eng")

    def test_unknown_zzz_skipped(self):
        r"""SC-3 (MUST PASS currently): Unknown [zzz] is skipped — code not in ISO 639-3.

        Regression guard — unknown codes must never produce Language rows.
        """
        mdf_data = "\\lx unknown_test\n\\so Unknown [zzz]\n\\ge test gloss"
        record = self._commit_mdf("unknown_test", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 0)

        lang = self.session.query(Language).filter_by(code="zzz").first()
        self.assertIsNone(lang)

    def test_french_mjy_skipped(self):
        r"""SC-4 (MUST PASS currently AND after fix): French [mjy] is skipped.

        Currently passes because "French != Mahican" hits the ref_name != lg_name guard.
        After fix, JaroWinkler("French", "Mahican") < 0.75 blocks it instead.
        This is a regression guard — it must pass before AND after.
        """
        mdf_data = "\\lx french_mjy_test\n\\so French [mjy]\n\\ge test gloss"
        record = self._commit_mdf("french_mjy_test", mdf_data)

        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 0)

        lang = self.session.query(Language).filter_by(code="mjy").first()
        self.assertIsNone(lang)


if __name__ == "__main__":
    unittest.main()
