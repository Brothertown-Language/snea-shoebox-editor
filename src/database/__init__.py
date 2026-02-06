# Copyright (c) 2026 Brothertown Language
"""
DATABASE SOURCE OF TRUTH: docs/database/DATABASE_SPECIFICATION.md
"""
from .connection import init_db, get_session, get_db_url, is_production, _auto_start_pgserver
from .base import Base
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
    'Record',
    'SearchEntry',
    'MatchupQueue',
    'EditHistory',
    'User',
    'UserActivityLog',
    'Permission',
    'SchemaVersion'
]
