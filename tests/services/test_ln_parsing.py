import unittest
import uuid
from src.database import get_session, Record, Language, RecordLanguage, MatchupQueue
from src.services.upload_service import UploadService

class TestLnParsing(unittest.TestCase):
    def setUp(self):
        self.session = get_session()
        # Clean up
        from src.database import EditHistory, SearchEntry, Source
        self.session.query(RecordLanguage).delete()
        self.session.query(EditHistory).delete()
        self.session.query(SearchEntry).delete()
        self.session.query(Record).delete()
        self.session.query(Language).delete()
        self.session.query(MatchupQueue).delete()
        self.session.query(Source).delete()
        self.session.commit()

        # Create a source
        self.source = Source(name="Test Source")
        self.session.add(self.source)
        self.session.flush()
        self.source_id = self.source.id

        # Create a default language
        self.default_lang = Language(name="Default", code="def")
        self.session.add(self.default_lang)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_ln_parsing_bulk_new(self):
        """Test that \ln tag is parsed correctly in bulk approve new."""
        mdf_data = "\\lx test\n\\ln Mohegan [moh]\n\\ge test gloss"
        batch_id = str(uuid.uuid4())
        
        # Stage entry
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx="test",
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        # Commit bulk new
        UploadService.commit_new(batch_id, "test@example.com", self.default_lang.id, str(uuid.uuid4()))

        # Verify record and language
        record = self.session.query(Record).filter_by(lx="test").first()
        self.assertIsNotNone(record)
        
        # Check associated languages
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        
        lang = self.session.query(Language).get(record_langs[0].language_id)
        self.assertEqual(lang.name, "Mohegan")
        self.assertEqual(lang.code, "moh")

    def test_legacy_lg_not_parsed(self):
        """Test that \lg tag is NO LONGER parsed."""
        mdf_data = "\\lx test2\n\\lg OldTag [old]\n\\ge test gloss"
        batch_id = str(uuid.uuid4())
        
        # Stage entry
        q_row = MatchupQueue(
            user_email="test@example.com",
            source_id=self.source_id,
            batch_id=batch_id,
            status="create_new",
            lx="test2",
            mdf_data=mdf_data
        )
        self.session.add(q_row)
        self.session.commit()

        # Commit bulk new
        UploadService.commit_new(batch_id, "test@example.com", self.default_lang.id, str(uuid.uuid4()))

        # Verify record and fallback language
        record = self.session.query(Record).filter_by(lx="test2").first()
        self.assertIsNotNone(record)
        
        record_langs = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(record_langs), 1)
        
        lang = self.session.query(Language).get(record_langs[0].language_id)
        # Should fall back to default because \lg is ignored
        self.assertEqual(lang.name, "Default")

if __name__ == "__main__":
    unittest.main()
