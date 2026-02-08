# Copyright (c) 2026 Brothertown Language
import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.services.identity_service import IdentityService
from src.database import User, UserActivityLog

class TestIdentityService(unittest.TestCase):
    def setUp(self):
        # Patch session_state
        self.patcher_session_state = patch("streamlit.session_state", {})
        self.mock_session_state = self.patcher_session_state.start()
        
        # Patch secrets
        self.patcher_secrets = patch("streamlit.secrets", {"github_oauth": {"user_info_url": "https://api.github.com/user"}})
        self.mock_secrets = self.patcher_secrets.start()

    def tearDown(self):
        self.patcher_session_state.stop()
        self.patcher_secrets.stop()

    @patch("src.services.identity_service.get_session")
    def test_sync_user_to_db_new_user(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Setup: user does not exist
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        user_info = {
            "id": 123,
            "login": "testuser",
            "name": "Test User"
        }
        email = "test@example.com"
        
        IdentityService.sync_user_to_db(user_info, email)
        
        # Verify a new User object was added
        args, _ = mock_session.add.call_args
        added_user = args[0]
        self.assertIsInstance(added_user, User)
        self.assertEqual(added_user.github_id, 123)
        self.assertEqual(added_user.username, "testuser")
        self.assertEqual(added_user.email, email)
        mock_session.commit.assert_called_once()

    @patch("src.services.identity_service.get_session")
    def test_sync_user_to_db_existing_user(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Setup: user exists
        existing_user = User(github_id=123, username="oldname", email="old@example.com")
        mock_session.query.return_value.filter_by.return_value.first.return_value = existing_user
        
        user_info = {
            "id": 123,
            "login": "newname",
            "name": "New Name"
        }
        email = "new@example.com"
        
        IdentityService.sync_user_to_db(user_info, email)
        
        self.assertEqual(existing_user.username, "newname")
        self.assertEqual(existing_user.email, email)
        self.assertEqual(existing_user.full_name, "New Name")
        mock_session.commit.assert_called_once()

    def test_is_identity_synchronized(self):
        self.assertFalse(IdentityService.is_identity_synchronized())
        
        self.mock_session_state["user_info"] = {}
        self.mock_session_state["user_orgs"] = []
        self.mock_session_state["user_teams"] = []
        
        self.assertTrue(IdentityService.is_identity_synchronized())

    def test_get_user_teams_and_orgs(self):
        self.mock_session_state["user_orgs"] = [{"login": "org1"}, {"login": "org2"}]
        self.mock_session_state["user_teams"] = [{"slug": "team1"}, {"slug": "team2"}]
        
        result = IdentityService.get_user_teams_and_orgs()
        self.assertEqual(result["organizations"], ["org1", "org2"])
        self.assertEqual(result["teams"], ["team1", "team2"])

    @patch("requests.get")
    def test_fetch_github_user_info_authorized(self, mock_get):
        # Mock responses
        mock_user = MagicMock()
        mock_user.json.return_value = {"id": 1, "login": "user", "email": "user@example.com"}
        
        mock_orgs = MagicMock()
        mock_orgs.json.return_value = [{"login": "Brothertown-Language"}]
        
        mock_teams = MagicMock()
        mock_teams.json.return_value = [{
            "slug": "proto-SNEA",
            "organization": {"login": "Brothertown-Language"}
        }]
        
        mock_emails = MagicMock()
        mock_emails.json.return_value = [{"email": "primary@example.com", "primary": True, "verified": True}]
        
        mock_get.side_effect = [mock_user, mock_orgs, mock_teams, mock_emails]
        
        with patch("src.services.security_manager.SecurityManager.get_user_role") as mock_get_role:
            mock_get_role.return_value = "editor"
            with patch.object(IdentityService, "sync_user_to_db") as mock_sync:
                with patch("src.services.audit_service.AuditService.log_activity") as mock_log:
                    success = IdentityService.fetch_github_user_info("fake_token")
                    
                    self.assertTrue(success)
                    self.assertEqual(st.session_state["user_info"]["login"], "user")
                    self.assertEqual(len(st.session_state["user_orgs"]), 1)
                    self.assertEqual(len(st.session_state["user_teams"]), 1)
                    mock_sync.assert_called_once()
                    mock_log.assert_called_once()
                    mock_get_role.assert_called_once()

    @patch("requests.get")
    def test_fetch_github_user_info_unauthorized(self, mock_get):
        # Mock responses
        mock_user = MagicMock()
        mock_user.json.return_value = {"id": 1, "login": "user"}
        
        mock_orgs = MagicMock()
        mock_orgs.json.return_value = []
        
        mock_teams = MagicMock()
        mock_teams.json.return_value = [{"slug": "some-other-team", "organization": {"login": "other-org"}}]
        
        mock_emails = MagicMock()
        mock_emails.json.return_value = []
        
        mock_get.side_effect = [mock_user, mock_orgs, mock_teams, mock_emails]
        
        with patch("src.services.security_manager.SecurityManager.get_user_role") as mock_get_role:
            mock_get_role.return_value = None
            success = IdentityService.fetch_github_user_info("fake_token")
            
            self.assertFalse(success)
            self.assertTrue(st.session_state.get("is_unauthorized"))
            mock_get_role.assert_called_once()
