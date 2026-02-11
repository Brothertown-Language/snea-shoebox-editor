# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import unittest
import os
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.upload_service import UploadService, _strip_diacritics


SAMPLE_FILE = Path("src/seed_data/natick_sample_100.txt")


class TestStripDiacritics(unittest.TestCase):
    def test_strips_combining_marks(self):
        self.assertEqual(_strip_diacritics("ēsh"), "esh")
        self.assertEqual(_strip_diacritics("nâne"), "nane")

    def test_no_diacritics_unchanged(self):
        self.assertEqual(_strip_diacritics("hello"), "hello")

    def test_empty_string(self):
        self.assertEqual(_strip_diacritics(""), "")


class TestParseUpload(unittest.TestCase):
    def test_valid_content(self):
        content = "\\lx test\n\\ps n\n\\ge thing"
        result = UploadService.parse_upload(content)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['lx'], 'test')

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            UploadService.parse_upload("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            UploadService.parse_upload("   \n\n  ")

    def test_no_valid_entries_raises(self):
        with self.assertRaises(ValueError):
            UploadService.parse_upload("just some random text\nno tags here")

    def test_multiple_entries(self):
        content = "\\lx word1\n\\ps n\n\\ge thing1\n\n\\lx word2\n\\ps v\n\\ge thing2"
        result = UploadService.parse_upload(content)
        self.assertEqual(len(result), 2)

    def test_sample_file(self):
        if not SAMPLE_FILE.exists():
            self.skipTest("Sample file not available")
        content = SAMPLE_FILE.read_text(encoding='utf-8')
        result = UploadService.parse_upload(content)
        self.assertEqual(len(result), 150)


class TestAssignHomonymNumbers(unittest.TestCase):
    def _make_entry(self, lx, hm_tag=None):
        lines = [f"\\lx {lx}"]
        if hm_tag is not None:
            lines.append(f"\\hm {hm_tag}")
        lines.append("\\ps n")
        lines.append("\\ge gloss")
        mdf = '\n'.join(lines)
        entry = {
            'lx': lx,
            'hm': int(hm_tag) if hm_tag else 1,
            'ps': 'n',
            'ge': 'gloss',
            'mdf_data': mdf,
            'record_id': None,
            'va': [], 'se': [], 'cf': [], 've': [],
        }
        return entry

    def test_no_homonyms_no_change(self):
        entries = [self._make_entry("word1"), self._make_entry("word2")]
        result = UploadService.assign_homonym_numbers(entries)
        # No \hm should be added since each lx is unique
        self.assertNotIn('\\hm', result[0]['mdf_data'])
        self.assertNotIn('\\hm', result[1]['mdf_data'])

    def test_two_homonyms_assigned(self):
        entries = [self._make_entry("esh"), self._make_entry("esh")]
        result = UploadService.assign_homonym_numbers(entries)
        self.assertEqual(result[0]['hm'], 1)
        self.assertEqual(result[1]['hm'], 2)
        self.assertIn('\\hm 1', result[0]['mdf_data'])
        self.assertIn('\\hm 2', result[1]['mdf_data'])

    def test_diacritics_stripped_grouping(self):
        entries = [self._make_entry("ēsh"), self._make_entry("esh")]
        result = UploadService.assign_homonym_numbers(entries)
        self.assertEqual(result[0]['hm'], 1)
        self.assertEqual(result[1]['hm'], 2)

    def test_preserves_existing_hm(self):
        entries = [self._make_entry("esh", hm_tag="2"), self._make_entry("esh")]
        result = UploadService.assign_homonym_numbers(entries)
        # First entry keeps hm=2, second gets hm=1 (next available)
        self.assertEqual(result[0]['hm'], 2)
        self.assertEqual(result[1]['hm'], 1)

    def test_three_homonyms(self):
        entries = [
            self._make_entry("esh"),
            self._make_entry("esh"),
            self._make_entry("esh"),
        ]
        result = UploadService.assign_homonym_numbers(entries)
        hms = sorted([e['hm'] for e in result])
        self.assertEqual(hms, [1, 2, 3])

    def test_hm_inserted_after_lx(self):
        entries = [self._make_entry("esh"), self._make_entry("esh")]
        result = UploadService.assign_homonym_numbers(entries)
        lines = result[0]['mdf_data'].split('\n')
        lx_idx = next(i for i, l in enumerate(lines) if l.startswith('\\lx '))
        self.assertTrue(lines[lx_idx + 1].startswith('\\hm '))

    def test_single_entry_no_hm(self):
        entries = [self._make_entry("unique")]
        result = UploadService.assign_homonym_numbers(entries)
        self.assertNotIn('\\hm', result[0]['mdf_data'])


class TestStageAndListBatches(unittest.TestCase):
    """Tests for stage_entries and list_pending_batches using a real pgserver DB."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            from src.database import Base

            cls.test_db_path = Path("tmp/test_upload_service_db")
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
            raise unittest.SkipTest("pgserver not available")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'pg_server'):
            cls.pg_server.cleanup()

    def setUp(self):
        self.session = self.Session()
        # Seed required FK rows
        from src.database import Source, Language, User
        if not self.session.query(User).filter_by(email='test@example.com').first():
            self.session.add(User(email='test@example.com', username='tester', github_id=1))
            self.session.commit()
        if not self.session.query(Source).filter_by(name='Test Source').first():
            self.session.add(Source(name='Test Source'))
            self.session.commit()
        if not self.session.query(Language).filter_by(code='alg').first():
            self.session.add(Language(code='alg', name='Algonquian'))
            self.session.commit()
        self.source_id = self.session.query(Source).filter_by(name='Test Source').first().id
        self.language_id = self.session.query(Language).filter_by(code='alg').first().id

    def tearDown(self):
        # Clean matchup_queue between tests
        from src.database import MatchupQueue
        self.session.query(MatchupQueue).delete()
        self.session.commit()
        self.session.close()

    def _patch_session(self):
        """Patch get_session to return our test session."""
        return patch('src.services.upload_service.get_session', return_value=self.Session())

    def test_stage_entries_creates_rows(self):
        entries = [
            {'lx': 'word1', 'mdf_data': '\\lx word1\n\\ps n\n\\ge thing'},
            {'lx': 'word2', 'mdf_data': '\\lx word2\n\\ps v\n\\ge act'},
        ]
        with self._patch_session():
            batch_id = UploadService.stage_entries(
                'test@example.com', self.source_id, entries, 'test.txt'
            )

        self.assertIsNotNone(batch_id)
        from src.database import MatchupQueue
        rows = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].status, 'pending')
        self.assertEqual(rows[0].filename, 'test.txt')

    def test_stage_entries_returns_uuid(self):
        entries = [{'lx': 'w', 'mdf_data': '\\lx w'}]
        with self._patch_session():
            batch_id = UploadService.stage_entries(
                'test@example.com', self.source_id, entries
            )
        # Validate it's a UUID
        uuid.UUID(batch_id)

    def test_list_pending_batches(self):
        entries = [{'lx': 'w1', 'mdf_data': '\\lx w1'}]
        with self._patch_session():
            batch_id = UploadService.stage_entries(
                'test@example.com', self.source_id, entries, 'file.txt'
            )
        with self._patch_session():
            batches = UploadService.list_pending_batches('test@example.com')

        self.assertEqual(len(batches), 1)
        b = batches[0]
        self.assertEqual(b['batch_id'], batch_id)
        self.assertEqual(b['source_name'], 'Test Source')
        self.assertEqual(b['filename'], 'file.txt')
        self.assertEqual(b['entry_count'], 1)
        self.assertIsNotNone(b['uploaded_at'])

    def test_list_pending_batches_empty_for_other_user(self):
        entries = [{'lx': 'w1', 'mdf_data': '\\lx w1'}]
        with self._patch_session():
            UploadService.stage_entries(
                'test@example.com', self.source_id, entries
            )
        with self._patch_session():
            batches = UploadService.list_pending_batches('other@example.com')
        self.assertEqual(len(batches), 0)

    def test_multiple_batches_ordered(self):
        entries = [{'lx': 'w1', 'mdf_data': '\\lx w1'}]
        with self._patch_session():
            batch1 = UploadService.stage_entries(
                'test@example.com', self.source_id, entries, 'first.txt'
            )
        with self._patch_session():
            batch2 = UploadService.stage_entries(
                'test@example.com', self.source_id, entries, 'second.txt'
            )
        with self._patch_session():
            batches = UploadService.list_pending_batches('test@example.com')
        self.assertEqual(len(batches), 2)
        # Newest first
        self.assertEqual(batches[0]['batch_id'], batch2)
        self.assertEqual(batches[1]['batch_id'], batch1)


class TestMatchAndCommitOperations(unittest.TestCase):
    """DB-backed tests for B-5 through B-10."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            from src.database import Base

            cls.test_db_path = Path("tmp/test_upload_match_db")
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
            raise unittest.SkipTest("pgserver not available")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'pg_server'):
            cls.pg_server.cleanup()

    def setUp(self):
        from src.database import Source, Language, User, Record, MatchupQueue, EditHistory, SearchEntry
        self.session = self.Session()
        # Clean all test data
        self.session.query(SearchEntry).delete()
        self.session.query(EditHistory).delete()
        self.session.query(MatchupQueue).delete()
        self.session.query(Record).delete()
        self.session.query(Source).filter(Source.name.like('Test%')).delete(synchronize_session='fetch')
        self.session.commit()

        # Seed
        if not self.session.query(User).filter_by(email='test@example.com').first():
            self.session.add(User(email='test@example.com', username='tester', github_id=1))
            self.session.commit()
        if not self.session.query(Language).filter_by(code='alg').first():
            self.session.add(Language(code='alg', name='Algonquian'))
            self.session.commit()

        src = Source(name='Test Source A')
        self.session.add(src)
        self.session.commit()
        self.source_id = src.id
        self.language_id = self.session.query(Language).filter_by(code='alg').first().id

    def tearDown(self):
        self.session.close()

    def _patch_session(self):
        return patch('src.services.upload_service.get_session', return_value=self.Session())

    def _add_record(self, lx, mdf_data, hm=1, ps='n', ge='gloss', source_id=None):
        from src.database import Record, RecordLanguage
        rec = Record(
            lx=lx, hm=hm, ps=ps, ge=ge,
            source_id=source_id or self.source_id,
            mdf_data=mdf_data,
        )
        self.session.add(rec)
        self.session.flush()
        
        # Add primary language entry
        rl = RecordLanguage(record_id=rec.id, language_id=self.language_id, is_primary=True)
        self.session.add(rl)
        
        self.session.commit()
        return rec

    def _stage(self, entries, filename='test.txt'):
        with self._patch_session():
            return UploadService.stage_entries(
                'test@example.com', self.source_id, entries, filename
            )

    # --- B-5: suggest_matches ---

    def test_suggest_matches_exact_lx(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['suggested_record_id'], rec.id)
        self.assertEqual(results[0]['match_type'], 'exact')

    def test_suggest_matches_base_form_fallback(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'ēsh', 'mdf_data': '\\lx ēsh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertEqual(results[0]['suggested_record_id'], rec.id)
        self.assertEqual(results[0]['match_type'], 'base_form')

    def test_suggest_matches_no_match(self):
        batch_id = self._stage([{'lx': 'xyz', 'mdf_data': '\\lx xyz\n\\ps n\n\\ge unknown'}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertEqual(len(results), 1)
        self.assertIsNone(results[0]['suggested_record_id'])

    def test_suggest_matches_record_id_match(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire\n\\nt Record: 999')
        # The record's actual id won't be 999, so use the real id
        mdf = f'\\lx esh\n\\ps n\n\\ge flame\n\\nt Record: {rec.id}'
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': mdf}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertEqual(results[0]['suggested_record_id'], rec.id)

    def test_suggest_matches_cross_source(self):
        from src.database import Source
        src_b = Source(name='Test Source B')
        self.session.add(src_b)
        self.session.commit()
        self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire', source_id=src_b.id)
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertIn('Test Source B', results[0]['cross_source_matches'])

    def test_suggest_matches_record_id_conflict(self):
        from src.database import Source
        src_b = Source(name='Test Source B')
        self.session.add(src_b)
        self.session.commit()
        other_rec = self._add_record('other', '\\lx other\n\\ps n\n\\ge thing', source_id=src_b.id)
        mdf = f'\\lx newword\n\\ps n\n\\ge stuff\n\\nt Record: {other_rec.id}'
        batch_id = self._stage([{'lx': 'newword', 'mdf_data': mdf}])
        with self._patch_session():
            results = UploadService.suggest_matches(batch_id)
        self.assertTrue(results[0]['record_id_conflict'])
        self.assertIn('Test Source B', results[0]['record_id_conflict_sources'])

    # --- B-5b: auto_remove_exact_duplicates ---

    def test_auto_remove_exact_duplicates(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        # Upload identical content (minus \nt Record:)
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge fire'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            result = UploadService.auto_remove_exact_duplicates(batch_id)
        self.assertEqual(result['removed_count'], 1)
        self.assertIn('esh', result['headwords'])

    def test_auto_remove_keeps_different_entries(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            result = UploadService.auto_remove_exact_duplicates(batch_id)
        self.assertEqual(result['removed_count'], 0)

    # --- B-5c: flag_hm_mismatches ---

    def test_flag_hm_mismatches(self):
        rec = self._add_record('esh', '\\lx esh\n\\hm 1\n\\ps n\n\\ge fire', hm=1)
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\hm 2\n\\ps n\n\\ge fire'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            flagged = UploadService.flag_hm_mismatches(batch_id)
        self.assertEqual(len(flagged), 1)
        self.assertTrue(flagged[0]['hm_mismatch'])

    def test_flag_hm_no_mismatch(self):
        rec = self._add_record('esh', '\\lx esh\n\\hm 1\n\\ps n\n\\ge fire', hm=1)
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\hm 1\n\\ps n\n\\ge fire'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            flagged = UploadService.flag_hm_mismatches(batch_id)
        self.assertEqual(len(flagged), 0)

    # --- B-5d: flag_headword_distance ---

    def test_flag_headword_distance(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        mdf = f'\\lx completely_different\n\\ps n\n\\ge fire\n\\nt Record: {rec.id}'
        batch_id = self._stage([{'lx': 'completely_different', 'mdf_data': mdf}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            flagged = UploadService.flag_headword_distance(batch_id)
        self.assertEqual(len(flagged), 1)
        self.assertGreater(flagged[0]['headword_distance'], 3)

    def test_flag_headword_distance_within_threshold(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        mdf = f'\\lx esh\n\\ps n\n\\ge fire\n\\nt Record: {rec.id}'
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': mdf}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            flagged = UploadService.flag_headword_distance(batch_id)
        self.assertEqual(len(flagged), 0)

    # --- B-5a: rematch_batch ---

    def test_rematch_batch(self):
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            results1 = UploadService.suggest_matches(batch_id)
        self.assertIsNone(results1[0]['suggested_record_id'])
        # Now add a matching record
        self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        with self._patch_session():
            results2 = UploadService.rematch_batch(batch_id)
        self.assertIsNotNone(results2[0]['suggested_record_id'])

    # --- B-6: confirm_match ---

    def test_confirm_match(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        with self._patch_session():
            UploadService.confirm_match(row.id)
        self.session.refresh(row)
        self.assertEqual(row.status, 'matched')

    def test_confirm_match_with_override(self):
        rec1 = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        rec2 = self._add_record('esh2', '\\lx esh2\n\\ps n\n\\ge fire2')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        with self._patch_session():
            UploadService.confirm_match(row.id, record_id=rec2.id)
        self.session.refresh(row)
        self.assertEqual(row.suggested_record_id, rec2.id)

    # --- B-6a: approve_all_new_source ---

    def test_approve_all_new_source(self):
        batch_id = self._stage([
            {'lx': 'w1', 'mdf_data': '\\lx w1'},
            {'lx': 'w2', 'mdf_data': '\\lx w2'},
        ])
        with self._patch_session():
            count = UploadService.approve_all_new_source(
                batch_id, 'test@example.com', self.language_id, 'sess1'
            )
        self.assertEqual(count, 2)
        from src.database import MatchupQueue
        rows = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        for r in rows:
            self.assertEqual(r.status, 'create_new')

    # --- B-6b: approve_all_by_record_match ---

    def test_approve_all_by_record_match(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([
            {'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'},
            {'lx': 'xyz', 'mdf_data': '\\lx xyz\n\\ps n\n\\ge unknown'},
        ])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            count = UploadService.approve_all_by_record_match(
                batch_id, 'test@example.com', self.language_id, 'sess1',
            )
        self.assertEqual(count, 1)
        from src.database import MatchupQueue
        # Matched row should be removed from queue (applied)
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].lx, 'xyz')
        # Existing record should be updated
        self.session.refresh(rec)
        self.assertIn('flame', rec.mdf_data)

    # --- B-6c: approve_non_matches_as_new ---

    def test_approve_non_matches_as_new(self):
        self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([
            {'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'},
            {'lx': 'xyz', 'mdf_data': '\\lx xyz\n\\ps n\n\\ge unknown'},
        ])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        with self._patch_session():
            count = UploadService.approve_non_matches_as_new(
                batch_id, 'test@example.com', self.language_id, 'sess1',
            )
        self.assertEqual(count, 1)
        # Non-matched row should be removed from queue (applied as new record)
        from src.database import MatchupQueue, Record
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].lx, 'esh')
        # New record should exist
        new_rec = self.session.query(Record).filter_by(lx='xyz').first()
        self.assertIsNotNone(new_rec)
        self.assertIn('unknown', new_rec.ge)

    # --- B-6d: mark_as_homonym ---

    def test_mark_as_homonym(self):
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        with self._patch_session():
            UploadService.mark_as_homonym(row.id)
        self.session.refresh(row)
        self.assertEqual(row.status, 'create_homonym')

    # --- B-7: ignore_entry ---

    def test_ignore_entry(self):
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        with self._patch_session():
            UploadService.ignore_entry(row.id)
        self.session.refresh(row)
        self.assertEqual(row.status, 'ignored')

    # --- B-7a: discard_marked ---

    def test_discard_marked(self):
        batch_id = self._stage([
            {'lx': 'w1', 'mdf_data': '\\lx w1'},
            {'lx': 'w2', 'mdf_data': '\\lx w2'},
            {'lx': 'w3', 'mdf_data': '\\lx w3'},
        ])
        from src.database import MatchupQueue
        rows = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).order_by(MatchupQueue.id).all()
        # Mark first two as discard
        with self._patch_session():
            UploadService.mark_as_discard(rows[0].id)
        with self._patch_session():
            UploadService.mark_as_discard(rows[1].id)
        with self._patch_session():
            count = UploadService.discard_marked(batch_id)
        self.assertEqual(count, 2)
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].lx, 'w3')

    def test_apply_single_discard(self):
        batch_id = self._stage([{'lx': 'unwanted', 'mdf_data': '\\lx unwanted\n\\ps n\\n\\ge junk'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'discard'
        self.session.commit()
        with self._patch_session():
            result = UploadService.apply_single(row.id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(result['action'], 'discarded')
        self.assertIsNone(result['record_id'])
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).count()
        self.assertEqual(remaining, 0)

    # --- B-7b: discard_all ---

    def test_discard_all(self):
        batch_id = self._stage([
            {'lx': 'w1', 'mdf_data': '\\lx w1'},
            {'lx': 'w2', 'mdf_data': '\\lx w2'},
        ])
        with self._patch_session():
            count = UploadService.discard_all(batch_id)
        self.assertEqual(count, 2)
        from src.database import MatchupQueue
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).count()
        self.assertEqual(remaining, 0)

    # --- B-7b: apply_single ---

    def test_apply_single_create_new(self):
        batch_id = self._stage([{'lx': 'newword', 'mdf_data': '\\lx newword\n\\ps n\n\\ge thing'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'create_new'
        self.session.commit()
        with self._patch_session():
            result = UploadService.apply_single(row.id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(result['action'], 'created')
        self.assertEqual(result['lx'], 'newword')
        from src.database import Record
        rec = self.session.get(Record, result['record_id'])
        self.assertIsNotNone(rec)
        self.assertIn('\\nt Record:', rec.mdf_data)

    def test_apply_single_matched(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'matched'
        self.session.commit()
        with self._patch_session():
            result = UploadService.apply_single(row.id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(result['action'], 'updated')
        self.session.refresh(rec)
        self.assertIn('flame', rec.mdf_data)

    def test_apply_single_pending_raises(self):
        batch_id = self._stage([{'lx': 'w', 'mdf_data': '\\lx w'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        with self._patch_session():
            with self.assertRaises(ValueError):
                UploadService.apply_single(row.id, 'test@example.com', self.language_id, 'sess1')

    def test_apply_single_create_homonym(self):
        self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge water'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'create_homonym'
        self.session.commit()
        with self._patch_session():
            result = UploadService.apply_single(row.id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(result['action'], 'created_homonym')
        from src.database import Record
        new_rec = self.session.get(Record, result['record_id'])
        self.assertEqual(new_rec.hm, 2)

    # --- B-8: commit_matched ---

    def test_commit_matched(self):
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge flame'}])
        with self._patch_session():
            UploadService.suggest_matches(batch_id)
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'matched'
        self.session.commit()
        with self._patch_session():
            count = UploadService.commit_matched(batch_id, 'test@example.com', 'sess1')
        self.assertEqual(count, 1)
        self.session.refresh(rec)
        self.assertIn('flame', rec.mdf_data)
        from src.database import EditHistory
        hist = self.session.query(EditHistory).filter_by(record_id=rec.id).first()
        self.assertIsNotNone(hist)
        # Queue row should be deleted
        remaining = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).count()
        self.assertEqual(remaining, 0)

    # --- B-8a: commit_homonyms ---

    def test_commit_homonyms(self):
        self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        batch_id = self._stage([{'lx': 'esh', 'mdf_data': '\\lx esh\n\\ps n\n\\ge water'}])
        from src.database import MatchupQueue
        row = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).first()
        row.status = 'create_homonym'
        self.session.commit()
        with self._patch_session():
            count = UploadService.commit_homonyms(batch_id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(count, 1)
        from src.database import Record
        homonyms = self.session.query(Record).filter_by(lx='esh', source_id=self.source_id).all()
        self.assertEqual(len(homonyms), 2)
        hms = sorted([r.hm for r in homonyms])
        self.assertEqual(hms, [1, 2])

    # --- B-9: commit_new ---

    def test_commit_new(self):
        batch_id = self._stage([
            {'lx': 'new1', 'mdf_data': '\\lx new1\n\\ps n\n\\ge thing1'},
            {'lx': 'new2', 'mdf_data': '\\lx new2\n\\ps v\n\\ge thing2'},
        ])
        with self._patch_session():
            count = UploadService.commit_new(batch_id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(count, 0) # Should be 0 as they are pending
        
        from src.database import MatchupQueue
        rows = self.session.query(MatchupQueue).filter_by(batch_id=batch_id).all()
        for row in rows:
            row.status = 'create_new'
        self.session.commit()

        with self._patch_session():
            count = UploadService.commit_new(batch_id, 'test@example.com', self.language_id, 'sess1')
        self.assertEqual(count, 2)
        from src.database import Record, EditHistory
        recs = self.session.query(Record).filter_by(source_id=self.source_id).all()
        self.assertEqual(len(recs), 2)
        for rec in recs:
            self.assertIn('\\nt Record:', rec.mdf_data)
            hist = self.session.query(EditHistory).filter_by(record_id=rec.id).first()
            self.assertIsNotNone(hist)
            self.assertEqual(hist.version, 1)

    # --- B-10: populate_search_entries ---

    def test_populate_search_entries(self):
        rec = self._add_record(
            'esh', '\\lx esh\n\\va ēsh\n\\se eshkw\n\\cf nane\n\\ve fire\n\\ps n\n\\ge fire'
        )
        with self._patch_session():
            count = UploadService.populate_search_entries([rec.id])
        self.assertEqual(count, 5)  # lx + va + se + cf + ve
        from src.database import SearchEntry
        entries = self.session.query(SearchEntry).filter_by(record_id=rec.id).all()
        types = sorted([e.entry_type for e in entries])
        self.assertEqual(types, ['cf', 'lx', 'se', 'va', 've'])

    def test_populate_search_entries_replaces_existing(self):
        from src.database import SearchEntry
        rec = self._add_record('esh', '\\lx esh\n\\ps n\n\\ge fire')
        self.session.add(SearchEntry(record_id=rec.id, term='old', entry_type='lx'))
        self.session.commit()
        with self._patch_session():
            count = UploadService.populate_search_entries([rec.id])
        self.assertEqual(count, 1)
        entries = self.session.query(SearchEntry).filter_by(record_id=rec.id).all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].term, 'esh')


if __name__ == '__main__':
    unittest.main()
