# Copyright (c) 2026 Brothertown Language
from typing import Dict, Any, List, Optional
from sqlalchemy import func, desc
from src.database.connection import get_session
from src.database.models.core import Record, Source, Language, RecordLanguage
from src.database.models.workflow import EditHistory
from src.logging_config import get_logger

logger = get_logger("snea.services.statistics")

class StatisticsService:
    """
    Service for retrieving linguistic and system statistics.
    """

    @classmethod
    def get_summary_stats(cls) -> Dict[str, int]:
        """
        Returns basic counts of records, sources, and languages.
        """
        with get_session() as session:
            try:
                record_count = session.query(func.count(Record.id)).scalar() or 0
                source_count = session.query(func.count(Source.id)).scalar() or 0
                
                # Count only languages that are actually assigned to records
                language_count = session.query(func.count(func.distinct(RecordLanguage.language_id))).scalar() or 0
                
                return {
                    "records": record_count,
                    "sources": source_count,
                    "languages": language_count
                }
            except Exception as e:
                logger.error(f"Error fetching summary stats: {e}")
                raise

    @classmethod
    def get_status_distribution(cls) -> Dict[str, int]:
        """
        Returns the distribution of records by status.
        """
        with get_session() as session:
            try:
                results = session.query(Record.status, func.count(Record.id)).group_by(Record.status).all()
                return {status: count for status, count in results}
            except Exception as e:
                logger.error(f"Error fetching status distribution: {e}")
                raise

    @classmethod
    def get_top_parts_of_speech(cls, limit: int = 10) -> Dict[str, int]:
        """
        Returns the most common parts of speech.
        """
        with get_session() as session:
            try:
                results = session.query(Record.ps, func.count(Record.id))\
                    .group_by(Record.ps)\
                    .order_by(desc(func.count(Record.id)))\
                    .limit(limit).all()
                return {ps if ps else "Unknown": count for ps, count in results}
            except Exception as e:
                logger.error(f"Error fetching POS distribution: {e}")
                raise

    @classmethod
    def get_source_distribution(cls) -> Dict[str, int]:
        """
        Returns the count of records per source.
        """
        with get_session() as session:
            try:
                results = session.query(Source.name, func.count(Record.id))\
                    .join(Record)\
                    .group_by(Source.name).all()
                return {name: count for name, count in results}
            except Exception as e:
                logger.error(f"Error fetching source distribution: {e}")
                raise

    @classmethod
    def get_language_distribution(cls, primary_only: bool = True) -> Dict[str, int]:
        """
        Returns the count of records per language.
        If primary_only is True, only counts is_primary=True mappings.
        """
        with get_session() as session:
            try:
                query = session.query(Language.name, func.count(RecordLanguage.id))\
                    .join(RecordLanguage)\
                    .group_by(Language.name)
                
                if primary_only:
                    query = query.filter(RecordLanguage.is_primary == True)
                    
                results = query.all()
                return {name: count for name, count in results}
            except Exception as e:
                logger.error(f"Error fetching language distribution: {e}")
                raise

    @classmethod
    def get_recent_activity(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Returns the most recent edits.
        """
        with get_session() as session:
            try:
                results = session.query(EditHistory)\
                    .order_by(desc(EditHistory.timestamp))\
                    .limit(limit).all()
                
                activity = []
                for entry in results:
                    activity.append({
                        "record_id": entry.record_id,
                        "lx": entry.record.lx if entry.record else "Unknown",
                        "user": entry.user_email,
                        "timestamp": entry.timestamp,
                        "summary": entry.change_summary
                    })
                return activity
            except Exception as e:
                logger.error(f"Error fetching recent activity: {e}")
                raise
