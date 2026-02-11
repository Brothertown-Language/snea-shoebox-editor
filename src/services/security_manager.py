# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from typing import Optional, List, Dict, Any
from src.database import get_session, Permission
from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
from src.logging_config import get_logger

logger = get_logger("snea.security")

class SecurityManager:
    """
    Centralized service for RBAC, session rehydration, and route protection.
    """

    @staticmethod
    def rehydrate_session():
        """
        Extract cookie-based rehydration logic from app.py.
        """
        if "cookie_controller" not in st.session_state:
            return

        controller = st.session_state["cookie_controller"]
        saved_token = controller.get(GH_AUTH_TOKEN_COOKIE)
        
        if saved_token and "auth" not in st.session_state:
            logger.debug("Rehydrating session from saved cookie token")
            st.session_state["auth"] = saved_token
            st.session_state.logged_in = True

    @staticmethod
    def get_user_role(user_teams: List[Dict[str, Any]]) -> Optional[str]:
        """
        Resolve the highest global role for a user based on their GitHub teams.
        """
        # Roles hierarchy: admin > editor > viewer
        role_hierarchy = {'admin': 3, 'editor': 2, 'viewer': 1}
        highest_role = None
        highest_weight = 0

        logger.debug("Resolving role for %d team(s)", len(user_teams))
        session = get_session()
        try:
            # Fetch all permissions from DB
            permissions = session.query(Permission).all()
            logger.debug("Loaded %d permission rule(s) from DB", len(permissions))
            
            for p in permissions:
                # Check if user is in the required team and org
                match = False
                for team in user_teams:
                    team_slug = team.get("slug")
                    # Use team slug or name for matching (slug is more reliable)
                    team_identifier = team_slug or team.get("name")
                    org_login = team.get("organization", {}).get("login")
                    
                    if p.github_team.lower() == team_identifier.lower() and p.github_org.lower() == org_login.lower():
                        match = True
                        break
                
                if match:
                    weight = role_hierarchy.get(p.role, 0)
                    if weight > highest_weight:
                        highest_weight = weight
                        highest_role = p.role
            
            logger.debug("Resolved role: %s", highest_role)
            return highest_role
        except Exception as e:
            logger.error("get_user_role failed: %s", e)
            return None
        finally:
            session.close()

    @staticmethod
    def check_permission(user_email: str, source_id: Optional[int], required_role: str) -> bool:
        """
        Check if a user has the required role for a specific source.
        If source_id is None, it checks for any permission matching the role.
        """
        role_hierarchy = {'admin': 3, 'editor': 2, 'viewer': 1}
        required_weight = role_hierarchy.get(required_role, 0)
        
        if "user_teams" not in st.session_state:
            return False

        user_teams = st.session_state["user_teams"]
        
        session = get_session()
        try:
            # Query permissions that match the user's teams/orgs
            # and satisfy the source_id (either specific or global)
            
            permissions = session.query(Permission).all()
            
            user_max_weight = 0
            for p in permissions:
                # Check source compatibility
                if source_id is not None and p.source_id is not None and p.source_id != source_id:
                    continue
                
                # Check team membership
                match = False
                for team in user_teams:
                    team_slug = team.get("slug")
                    team_identifier = team_slug or team.get("name")
                    org_login = team.get("organization", {}).get("login")
                    
                    if p.github_team.lower() == team_identifier.lower() and p.github_org.lower() == org_login.lower():
                        match = True
                        break
                
                if match:
                    user_max_weight = max(user_max_weight, role_hierarchy.get(p.role, 0))
            
            return user_max_weight >= required_weight
        except Exception as e:
            logger.error("check_permission failed: %s", e)
            return False
        finally:
            session.close()
