# Copyright (c) 2026 Brothertown Language
"""
Authentication utilities for GitHub OAuth.
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List
from src.services.identity_service import IdentityService
from src.services.audit_service import AuditService

def is_identity_synchronized() -> bool:
    """
    Check if all critical GitHub identity information (profile, organizations, and teams) is present in the session state.
    """
    return IdentityService.is_identity_synchronized()

def fetch_github_user_info(access_token: str) -> bool:
    """
    Fetch user profile, organizations, teams, and primary email from GitHub and store in session state.
    Performs mandatory team membership verification (Brothertown-Language/proto-SNEA).
    Returns True if successful and authorized, False otherwise.
    """
    return IdentityService.fetch_github_user_info(access_token)

def log_user_activity(email: str, action: str, details: Optional[str] = None) -> None:
    """
    Log a user activity to the database.
    """
    AuditService.log_activity(email, action, details)

def sync_user_to_db(user_info: Dict[str, Any], email: str) -> None:
    """
    Update or create the user record in the database.
    """
    IdentityService.sync_user_to_db(user_info, email)
