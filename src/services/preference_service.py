# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from typing import Optional
from src.database import get_session, UserPreference
from src.logging_config import get_logger

logger = get_logger("snea.preference_service")

class PreferenceService:
    """
    Manages persistent user preferences (UI settings, defaults, etc.) in the database.
    """

    @staticmethod
    def get_preference(user_email: str, view_name: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a saved preference for a user and view.
        Returns the default value if no preference is found or if an error occurs.
        """
        session = get_session()
        try:
            pref = (
                session.query(UserPreference)
                .filter_by(user_email=user_email, view_name=view_name, preference_key=key)
                .first()
            )
            return pref.preference_value if pref else default
        except Exception as e:
            logger.error(f"Failed to get preference {key} for {user_email} in {view_name}: {e}")
            return default
        finally:
            session.close()

    @staticmethod
    def set_preference(user_email: str, view_name: str, key: str, value: str) -> bool:
        """
        Upserts a preference in the database.
        Returns True if successful, False otherwise.
        """
        session = get_session()
        try:
            # Try to find existing preference
            pref = (
                session.query(UserPreference)
                .filter_by(user_email=user_email, view_name=view_name, preference_key=key)
                .first()
            )

            if pref:
                pref.preference_value = value
            else:
                new_pref = UserPreference(
                    user_email=user_email,
                    view_name=view_name,
                    preference_key=key,
                    preference_value=value
                )
                session.add(new_pref)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to set preference {key}={value} for {user_email} in {view_name}: {e}")
            return False
        finally:
            session.close()
