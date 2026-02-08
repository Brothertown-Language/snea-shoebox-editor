# Copyright (c) 2026 Brothertown Language
import os
import sys
from pathlib import Path
import streamlit as st
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Mock streamlit session state
if "session_state" not in st.__dict__:
    st.session_state = {}

from src.database.connection import init_db, get_session
from src.database.models.identity import Permission, User
from src.database.models.core import Source
from src.services.security_manager import SecurityManager

def test_security_manager():
    print("Starting SecurityManager test...")
    
    # Ensure we are using the private database
    os.environ["JUNIE_PRIVATE_DB"] = "true"
    
    # Initialize the database
    engine = init_db()
    
    session = get_session()
    try:
        # 1. Setup mock session state
        st.session_state["user_teams"] = [
            {"slug": "proto-SNEA-admin", "organization": {"login": "Brothertown-Language"}}
        ]
        st.session_state["user_info"] = {"email": "admin@example.com"}
        
        # 2. Test get_user_role (case-insensitive)
        st.session_state["user_teams"] = [
            {"slug": "PROTO-SNEA-ADMIN", "organization": {"login": "BROTHERTOWN-LANGUAGE"}}
        ]
        role = SecurityManager.get_user_role(st.session_state["user_teams"])
        print(f"Role for admin user (case-insensitive test): {role}")
        assert role == "admin", f"Expected admin, got {role}"
        
        # 3. Test check_permission (global, case-insensitive)
        has_perm = SecurityManager.check_permission("admin@example.com", None, "admin")
        print(f"Admin has admin perm (case-insensitive test): {has_perm}")
        assert has_perm is True
        
        has_perm = SecurityManager.check_permission("admin@example.com", None, "editor")
        print(f"Admin has editor perm: {has_perm}")
        assert has_perm is True
        
        # 4. Test with non-admin team
        st.session_state["user_teams"] = [
            {"slug": "proto-SNEA", "organization": {"login": "Brothertown-Language"}}
        ]
        role = SecurityManager.get_user_role(st.session_state["user_teams"])
        print(f"Role for editor user: {role}")
        assert role == "editor", f"Expected editor, got {role}"
        
        has_perm = SecurityManager.check_permission("editor@example.com", None, "admin")
        print(f"Editor has admin perm: {has_perm}")
        assert has_perm is False
        
        has_perm = SecurityManager.check_permission("editor@example.com", None, "editor")
        print(f"Editor has editor perm: {has_perm}")
        assert has_perm is True

        # 5. Test with specific source permission
        # Check if source exists
        source = session.query(Source).filter_by(name="Test Source").first()
        if not source:
            source = Source(name="Test Source", short_name="TS")
            session.add(source)
            session.commit()
        
        # Add a specific permission
        # Use a unique team name for this test
        test_team_name = "test-team-unique-123"
        spec_perm = session.query(Permission).filter_by(github_team=test_team_name).first()
        if not spec_perm:
            spec_perm = Permission(
                source_id=source.id,
                github_org="Brothertown-Language",
                github_team=test_team_name,
                role="editor"
            )
            session.add(spec_perm)
            session.commit()
        
        st.session_state["user_teams"] = [
            {"slug": test_team_name, "organization": {"login": "Brothertown-Language"}}
        ]
        
        # Should have permission for this source
        has_perm = SecurityManager.check_permission("user@example.com", source.id, "editor")
        print(f"User in test-team has editor perm for source {source.id}: {has_perm}")
        assert has_perm is True
        
        # Should NOT have permission for a different source (if it existed)
        has_perm = SecurityManager.check_permission("user@example.com", 999, "editor")
        print(f"User in test-team has editor perm for source 999: {has_perm}")
        assert has_perm is False
        
        # 6. Test rehydrate_session
        from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
        mock_controller = MagicMock()
        mock_controller.get.return_value = {"token": {"access_token": "fake_token"}}
        st.session_state["cookie_controller"] = mock_controller
        st.session_state.logged_in = False
        if "auth" in st.session_state:
            del st.session_state["auth"]
            
        SecurityManager.rehydrate_session()
        print(f"Rehydrated logged_in: {st.session_state.logged_in}")
        assert st.session_state.logged_in is True
        assert st.session_state["auth"] == {"token": {"access_token": "fake_token"}}

        print("SUCCESS: SecurityManager tests passed.")
            
    finally:
        session.close()

if __name__ == "__main__":
    test_security_manager()
