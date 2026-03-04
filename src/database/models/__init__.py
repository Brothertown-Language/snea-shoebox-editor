# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# CONVENTION: Every new SQLAlchemy model class MUST include __table_args__ with 'extend_existing': True.
# - Simple table (no other constraints): __table_args__ = {'extend_existing': True}
# - Table with constraints (e.g. UniqueConstraint): __table_args__ = (UniqueConstraint(...), {'extend_existing': True})
# This prevents sqlalchemy.exc.InvalidRequestError on Streamlit hot-reload / module re-import.
from .core import Source, Language, RecordLanguage, Record
from .search import SearchEntry
from .workflow import MatchupQueue, EditHistory
from .identity import User, UserPreference, UserActivityLog, Permission
from .meta import SchemaVersion
from .iso639 import ISO639_3

__all__ = [
    'Source',
    'Language',
    'RecordLanguage',
    'Record',
    'SearchEntry',
    'MatchupQueue',
    'EditHistory',
    'User',
    'UserPreference',
    'UserActivityLog',
    'Permission',
    'SchemaVersion',
    'ISO639_3'
]
