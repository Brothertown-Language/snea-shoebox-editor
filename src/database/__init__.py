"""Database package — connection, models, and migrations.

Import from concrete modules:
    from src.database.connection import get_session, init_db, get_db_url, is_production
    from src.database.base import Base
    from src.database.models.core import Record, Source, Language, RecordLanguage
    from src.database.models.search import SearchEntry, HeadwordSearchEntry, GlossSearchEntry
    from src.database.models.workflow import MatchupQueue, EditHistory
    from src.database.models.identity import User, Permission, UserPreference, UserActivityLog
    from src.database.models.meta import SchemaVersion
    from src.database.models.iso639 import ISO639_3
"""
