# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import datetime
import streamlit as st
from src.database import get_session, User
from src.frontend.ui_utils import handle_ui_error
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, Dict, Any

def login_user_simple(username: str):
    """Login or create a user based on username and set the session."""
    if not username:
        st.error("Invalid username")
        return None

    db: Session = get_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            # Create new user
            user = User(
                github_id=0, # Placeholder
                email=f"{username}@example.com",
                username=username,
                full_name=username,
                last_login=func.now()
            )
            db.add(user)
        else:
            if not user.is_active:
                st.error("Account is disabled. Please contact an administrator.")
                return None
            # Update last login
            user.last_login = func.now()
        
        db.commit()
        db.refresh(user)
        
        # Set session state
        st.session_state.user = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email
        }
        st.session_state.authenticated = True
        
        return user
    except Exception as e:
        db.rollback()
        handle_ui_error(e, "Database error during login.", logger_name="snea.auth")
        return None
    finally:
        db.close()

def login_user(github_user_data: Dict[str, Any]):
    """Login or create a user based on GitHub data and set the session."""
    github_id = github_user_data.get("id")
    email = github_user_data.get("email")
    username = github_user_data.get("login")
    name = github_user_data.get("name")

    if not github_id or not username:
        st.error("Invalid GitHub user data")
        return None

    db: Session = get_session()
    try:
        user = db.query(User).filter(User.github_id == github_id).first()
        if not user:
            # Create new user
            user = User(
                github_id=github_id,
                email=email or f"{username}@github.com",
                username=username,
                full_name=name,
                last_login=func.now()
            )
            db.add(user)
        else:
            if not user.is_active:
                st.error("Account is disabled. Please contact an administrator.")
                return None
            # Update last login
            user.last_login = func.now()
            if email:
                user.email = email
            if name:
                user.full_name = name
        
        db.commit()
        db.refresh(user)
        
        # Set session state
        st.session_state.user = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email
        }
        st.session_state.authenticated = True
        
        return user
    except Exception as e:
        db.rollback()
        handle_ui_error(e, "Database error during login.", logger_name="snea.auth")
        return None
    finally:
        db.close()

def logout_user():
    """Logout the current user."""
    st.session_state.authenticated = False
    st.session_state.user = None

def check_auth():
    """Check if the user is authenticated via session state."""
    return st.session_state.get("authenticated", False)
