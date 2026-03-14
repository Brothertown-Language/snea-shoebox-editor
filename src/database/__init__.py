# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from .connection import init_db, get_session, get_db_url, is_production, _auto_start_pgserver
from .base import Base  # safe here: connection.py imports Base lazily (lazy-import standard)
from .models import *

__all__ = [
    'init_db',
    'get_session',
    'get_db_url',
    'is_production',
    '_auto_start_pgserver',
    'Base',
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
    'SchemaVersion'
]
