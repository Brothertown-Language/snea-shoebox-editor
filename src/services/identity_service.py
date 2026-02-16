# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Identity Service for managing GitHub user identity and database synchronization.
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List
from src.database import get_session, User
from sqlalchemy.sql import func
from src.services.audit_service import AuditService
from src.logging_config import get_logger

logger = get_logger("snea.identity")

class IdentityService:
    """
    Service for centralizing GitHub identity synchronization and team resolution.
    """

    @staticmethod
    def is_identity_synchronized() -> bool:
        """
        Check if all critical GitHub identity information (profile, organizations, and teams) is present in the session state.
        """
        return all(key in st.session_state for key in ["user_info", "user_orgs", "user_teams"])

    @staticmethod
    def fetch_github_user_info(access_token: str) -> bool:
        """
        Fetch user profile, organizations, teams, and primary email from GitHub and store in session state.
        Performs mandatory team membership verification (Brothertown-Language/proto-SNEA).
        Returns True if successful and authorized, False otherwise.
        """
        logger.debug("Fetching GitHub user info")
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        base_url = st.secrets["github_oauth"]["user_info_url"]

        try:
            # Fetch user profile
            user_response = requests.get(base_url, headers=headers, timeout=10)
            user_response.raise_for_status()
            user_info = user_response.json()
            st.session_state["user_info"] = user_info
            
            logger.info("Fetched GitHub user info for: %s", user_info.get('login'))

            # Fetch organizations
            orgs_response = requests.get(f"{base_url}/orgs", headers=headers, timeout=10)
            orgs_response.raise_for_status()
            st.session_state["user_orgs"] = orgs_response.json()

            # Fetch teams
            teams_response = requests.get(f"{base_url}/teams", headers=headers, timeout=10)
            teams_response.raise_for_status()
            user_teams = teams_response.json()
            st.session_state["user_teams"] = user_teams

            # Fetch user emails to get the primary email
            emails_response = requests.get(f"{base_url}/emails", headers=headers, timeout=10)
            emails_response.raise_for_status()
            emails = emails_response.json()
            
            primary_email = None
            for email_record in emails:
                if email_record.get("primary") and email_record.get("verified"):
                    primary_email = email_record.get("email")
                    break
            
            # Fallback to the email in user_info if no primary/verified found
            if not primary_email:
                primary_email = user_info.get("email")

            # Verify authorization against the permissions table
            from src.services.security_manager import SecurityManager
            user_role = SecurityManager.get_user_role(user_teams)
            
            if not user_role:
                logger.debug("User not authorized. Teams: %s", [t.get('slug') or t.get('name') for t in user_teams])
                st.session_state["is_unauthorized"] = True
                return False

            # Cache user role for navigation and access control
            st.session_state["user_role"] = user_role

            # Debug: log identity details
            logger.debug("User email: %s, username: %s, orgs: %s, teams: %s",
                         primary_email,
                         user_info.get('login'),
                         [o.get('login') for o in st.session_state.get('user_orgs', [])],
                         [t.get('slug') for t in user_teams])

            # If authorized, sync user to database
            if primary_email:
                st.session_state["user_email"] = primary_email
                IdentityService.sync_user_to_db(user_info, primary_email)
                
                # Log the login activity
                logger.debug("User logged in: %s", primary_email)
                AuditService.log_activity(primary_email, "login", "User logged in via GitHub OAuth")
            else:
                st.warning("Could not determine user email. Audit trail might be limited.")

            return True

        except Exception as e:
            st.error(f"Failed to fetch user information from GitHub: {e}")
            return False

    @staticmethod
    def sync_user_to_db(user_info: Dict[str, Any], email: str) -> None:
        """
        Update or create the user record in the database.
        """
        github_id = user_info.get("id")
        username = user_info.get("login")
        full_name = user_info.get("name")

        if not github_id or not username:
            return

        session = get_session()
        try:
            # Try to find user by github_id (primary lookup as per issue)
            user = session.query(User).filter_by(github_id=github_id).first()
            
            if user:
                # Update existing user by GitHub ID
                user.email = email
                user.username = username
                user.full_name = full_name
                user.last_login = func.now()
            else:
                # Check if email is already used by another account.
                # If the email matches but the GitHub ID is different, we assume the email is 
                # authoritative (e.g., the user created a new GitHub account but kept their email).
                # We update the existing record to match the new GitHub identity.
                existing_email_user = session.query(User).filter_by(email=email).first()
                if existing_email_user:
                    logger.info("Email collision detected for %s. Updating GitHub ID from %s to %s.", 
                                email, existing_email_user.github_id, github_id)
                    existing_email_user.github_id = github_id
                    existing_email_user.username = username
                    existing_email_user.full_name = full_name
                    existing_email_user.last_login = func.now()
                else:
                    # Create new user if neither ID nor Email exists
                    user = User(
                        email=email,
                        username=username,
                        github_id=github_id,
                        full_name=full_name,
                        last_login=func.now()
                    )
                    session.add(user)
            
            session.commit()
        except Exception as e:
            session.rollback()
            st.error(f"Failed to sync user to database: {e}")
            logger.error("sync_user_to_db failed: %s", e)
        finally:
            session.close()

    @staticmethod
    def get_user_teams_and_orgs() -> Dict[str, List[str]]:
        """
        Return structured data of user's teams and organizations.
        """
        orgs = [org.get("login") for org in st.session_state.get("user_orgs", [])]
        teams = [team.get("slug") for team in st.session_state.get("user_teams", [])]
        return {
            "organizations": orgs,
            "teams": teams
        }

    @staticmethod
    @st.cache_data
    def get_github_username(email: str) -> Optional[str]:
        """
        Fetch the GitHub username for a given email address.
        Cached to minimize database hits.
        """
        if not email:
            return None
        
        session = get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            return user.username if user else None
        except Exception as e:
            logger.error("Failed to fetch github username for %s: %s", email, e)
            return None
        finally:
            session.close()

    @staticmethod
    def sync_identity(access_token: str) -> bool:
        """
        Orchestrate the synchronization of GitHub identity.
        Used in app.py and login.py.
        """
        if not IdentityService.is_identity_synchronized():
            logger.debug("Identity not yet synchronized, fetching from GitHub")
            return IdentityService.fetch_github_user_info(access_token)
        logger.debug("Identity already synchronized, skipping fetch")
        return True
