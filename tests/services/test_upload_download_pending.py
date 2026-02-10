# Copyright (c) 2026 Brothertown Language
import unittest
import uuid
from src.services.upload_service import UploadService
from src.database import get_session, MatchupQueue, Source, User

class TestUploadDownloadPending(unittest.TestCase):
    def setUp(self):
        # We assume tests are run with JUNIE_PRIVATE_DB=true
        pass

    def test_get_pending_batch_mdf(self):
        """Test retrieving pending records for a batch as MDF text."""
        session = get_session()
        try:
            # Setup test data
            user_email = f"test-{uuid.uuid4()}@example.com"
            user = User(email=user_email, username=f"user-{uuid.uuid4()}", github_id=int(uuid.uuid4().int % 2147483647))
            session.add(user)
            session.commit()

            source = Source(name=f"Source {uuid.uuid4()}")
            session.add(source)
            session.commit()
            
            batch_id = str(uuid.uuid4())
            
            q1 = MatchupQueue(
                batch_id=batch_id,
                user_email=user_email,
                source_id=source.id,
                lx="test1",
                mdf_data="\\lx test1\n\\ge gloss1",
                status="pending"
            )
            q2 = MatchupQueue(
                batch_id=batch_id,
                user_email=user_email,
                source_id=source.id,
                lx="test2",
                mdf_data="\\lx test2\n\\ge gloss2",
                status="matched" # Should be included because it's still in matchup_queue (pending apply)
            )
            q3 = MatchupQueue(
                batch_id=batch_id,
                user_email=user_email,
                source_id=source.id,
                lx="test3",
                mdf_data="\\lx test3\n\\ge gloss3",
                status="discard" # Should NOT be included
            )
            
            session.add_all([q1, q2, q3])
            session.commit()
            
            # Execute
            mdf_content = UploadService.get_pending_batch_mdf(batch_id)
            
            # Verify
            self.assertIn("\\lx test1", mdf_content)
            self.assertIn("\\ge gloss1", mdf_content)
            self.assertIn("\\lx test2", mdf_content)
            self.assertIn("\\ge gloss2", mdf_content)
            self.assertNotIn("\\lx test3", mdf_content)
            self.assertNotIn("\\ge gloss3", mdf_content)
            
            # Verify separation
            self.assertIn("\n\n", mdf_content)
            
        finally:
            session.close()
