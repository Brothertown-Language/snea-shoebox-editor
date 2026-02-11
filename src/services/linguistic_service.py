# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Linguistic Service for CRUD operations on Record, Source, and Language models.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.database.connection import get_session
from src.database.models.core import Source, Record, Language
from src.logging_config import get_logger

logger = get_logger("snea.linguistic_service")

class LinguisticService:
    """
    Service for centralizing data access to linguistic models (Record, Source, Language).
    """

    @staticmethod
    def get_sources_with_counts() -> List[Dict[str, Any]]:
        """
        Retrieve all sources with their associated record counts.
        """
        with get_session() as session:
            # Subquery to count records per source
            count_subquery = (
                session.query(
                    Record.source_id,
                    func.count(Record.id).label('record_count')
                )
                .group_by(Record.source_id)
                .subquery()
            )

            # Join sources with the counts
            query = (
                session.query(
                    Source,
                    func.coalesce(count_subquery.c.record_count, 0).label('record_count')
                )
                .outerjoin(count_subquery, Source.id == count_subquery.c.source_id)
                .order_by(Source.name)
            )

            results = []
            for source, count in query.all():
                results.append({
                    "id": source.id,
                    "name": source.name,
                    "short_name": source.short_name,
                    "description": source.description,
                    "record_count": count
                })
            return results

    @staticmethod
    def update_source(source_id: int, **fields: Any) -> bool:
        """
        Update an existing source.
        """
        with get_session() as session:
            source = session.query(Source).filter(Source.id == source_id).first()
            if not source:
                logger.error(f"Source with ID {source_id} not found.")
                return False
            
            for key, value in fields.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            
            try:
                session.commit()
                logger.info(f"Updated source {source_id}: {fields}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update source {source_id}: {e}")
                return False

    @staticmethod
    def reassign_records(from_source_id: int, to_source_id: int) -> int:
        """
        Reassign all records from one source to another.
        Returns the number of records reassigned.
        """
        with get_session() as session:
            # Ensure target source exists
            target = session.query(Source).filter(Source.id == to_source_id).first()
            if not target:
                logger.error(f"Target source ID {to_source_id} does not exist.")
                return 0
            
            try:
                rows_updated = (
                    session.query(Record)
                    .filter(Record.source_id == from_source_id)
                    .update({Record.source_id: to_source_id}, synchronize_session=False)
                )
                session.commit()
                logger.info(f"Reassigned {rows_updated} records from source {from_source_id} to {to_source_id}.")
                return rows_updated
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to reassign records: {e}")
                return 0

    @staticmethod
    def delete_source(source_id: int) -> bool:
        """
        Delete a source if it has no associated records.
        """
        with get_session() as session:
            # Explicit check for records
            record_count = session.query(Record).filter(Record.source_id == source_id).count()
            if record_count > 0:
                logger.warning(f"Cannot delete source {source_id}: it has {record_count} records.")
                return False
            
            source = session.query(Source).filter(Source.id == source_id).first()
            if not source:
                return False
            
            try:
                session.delete(source)
                session.commit()
                logger.info(f"Deleted source {source_id}.")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to delete source {source_id}: {e}")
                return False

    @staticmethod
    def get_record(record_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single record by ID."""
        raise NotImplementedError("LinguisticService.get_record is not yet implemented.")

    @staticmethod
    def get_source(source_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single source by ID."""
        raise NotImplementedError("LinguisticService.get_source is not yet implemented.")

    @staticmethod
    def search_records(**filters: Any) -> List[Dict[str, Any]]:
        """Search records with optional filters (language, source, status, etc.)."""
        raise NotImplementedError("LinguisticService.search_records is not yet implemented.")

    @staticmethod
    def create_record(**fields: Any) -> Dict[str, Any]:
        """Create a new record."""
        raise NotImplementedError("LinguisticService.create_record is not yet implemented.")

    @staticmethod
    def update_record(record_id: int, **fields: Any) -> Dict[str, Any]:
        """Update an existing record."""
        raise NotImplementedError("LinguisticService.update_record is not yet implemented.")

    @staticmethod
    def soft_delete_record(record_id: int) -> None:
        """Soft-delete a record by setting is_deleted=True."""
        raise NotImplementedError("LinguisticService.soft_delete_record is not yet implemented.")
