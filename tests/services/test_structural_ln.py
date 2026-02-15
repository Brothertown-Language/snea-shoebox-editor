
import unittest
import os
from src.database import get_session, Record, Source
from src.services.upload_service import UploadService
from src.database.models.core import RecordLanguage, Language

class TestStructuralLanguageParsing(unittest.TestCase):
    def setUp(self):
        self.session = get_session()
        # Create a test source
        self.source = Source(name="Test Structural Source")
        self.session.add(self.source)
        self.session.commit()
        self.source_id = self.source.id

    def tearDown(self):
        self.session.query(RecordLanguage).delete()
        self.session.query(Record).delete()
        self.session.query(Language).delete()
        self.session.query(Source).delete()
        self.session.commit()
        self.session.close()

    def test_subentry_ln_not_primary(self):
        """Test that \ln in a subentry is NOT marked as primary if headword has no \ln."""
        mdf_data = "\\lx headword\n\\ge gloss\n\\se subentry\n\\ln Mohegan [moh]"
        
        from src.mdf.parser import parse_mdf
        parsed = parse_mdf(mdf_data)
        self.assertEqual(len(parsed), 1)
        entry = parsed[0]
        
        record = Record(
            lx=entry['lx'],
            hm=entry.get('hm', 1),
            source_id=self.source_id,
            mdf_data=mdf_data
        )
        self.session.add(record)
        self.session.flush()
        
        UploadService._update_record_languages(self.session, record, entry.get('lg', []))
        self.session.commit()
        
        # Check record_languages
        rls = self.session.query(RecordLanguage).filter_by(record_id=record.id).all()
        self.assertEqual(len(rls), 1)
        # Should now be FALSE because it's in a subentry and headword has no \ln
        self.assertFalse(rls[0].is_primary) 
        
    def test_headword_ln_is_primary(self):
        """Test that \ln in headword IS marked as primary."""
        mdf_data = "\\lx headword\n\\ln Mohegan [moh]\n\\ge gloss\n\\se subentry\n\\ln Cree [cre]"
        
        from src.mdf.parser import parse_mdf
        parsed = parse_mdf(mdf_data)
        entry = parsed[0]
        
        record = Record(
            lx=entry['lx'],
            hm=entry.get('hm', 1),
            source_id=self.source_id,
            mdf_data=mdf_data
        )
        self.session.add(record)
        self.session.flush()
        
        UploadService._update_record_languages(self.session, record, entry.get('lg', []))
        self.session.commit()
        
        rls = self.session.query(RecordLanguage).filter_by(record_id=record.id).order_by(RecordLanguage.id).all()
        self.assertEqual(len(rls), 2)
        # Mohegan (first) should be primary
        self.assertTrue(rls[0].is_primary)
        # Cree (second) should not be primary
        self.assertFalse(rls[1].is_primary)
        
if __name__ == "__main__":
    unittest.main()
