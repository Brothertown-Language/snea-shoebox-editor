# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Linguistic Service for CRUD operations on Record, Source, and Language models.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from src.database.connection import get_session
from src.database.models.core import Source, Record, Language
from src.database.models.workflow import MatchupQueue
from src.database.models.search import SearchEntry
from src.logging_config import get_logger

logger = get_logger("snea.linguistic_service")

@dataclass
class RecordSearchResult:
    """
    Container for search results and metadata for pagination.
    """
    records: List[Dict[str, Any]]
    total_count: int
    limit: int
    offset: int

class LinguisticService:
    """
    Service for centralizing data access to linguistic models (Record, Source, Language).
    """

    @staticmethod
    def get_sources_with_counts() -> List[Dict[str, Any]]:
        """
        Retrieve all sources with their associated record counts (Records + MatchupQueue).
        """
        with get_session() as session:
            # Subquery to count records per source
            record_counts = (
                session.query(
                    Record.source_id,
                    func.count(Record.id).label('record_count')
                )
                .group_by(Record.source_id)
                .subquery()
            )

            # Subquery to count matchup queue entries per source
            matchup_counts = (
                session.query(
                    MatchupQueue.source_id,
                    func.count(MatchupQueue.id).label('matchup_count')
                )
                .group_by(MatchupQueue.source_id)
                .subquery()
            )

            # Join sources with both counts and sum them
            query = (
                session.query(
                    Source,
                    (
                        func.coalesce(record_counts.c.record_count, 0) +
                        func.coalesce(matchup_counts.c.matchup_count, 0)
                    ).label('total_count')
                )
                .outerjoin(record_counts, Source.id == record_counts.c.source_id)
                .outerjoin(matchup_counts, Source.id == matchup_counts.c.source_id)
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
        Reassign all records and matchup queue entries from one source to another.
        Returns the total number of items reassigned.
        """
        with get_session() as session:
            # Ensure target source exists
            target = session.query(Source).filter(Source.id == to_source_id).first()
            if not target:
                logger.error(f"Target source ID {to_source_id} does not exist.")
                return 0
            
            try:
                # Reassign records
                rows_updated = (
                    session.query(Record)
                    .filter(Record.source_id == from_source_id)
                    .update({Record.source_id: to_source_id}, synchronize_session=False)
                )
                
                # Reassign matchup queue entries
                matchup_updated = (
                    session.query(MatchupQueue)
                    .filter(MatchupQueue.source_id == from_source_id)
                    .update({MatchupQueue.source_id: to_source_id}, synchronize_session=False)
                )
                
                session.commit()
                total_updated = rows_updated + matchup_updated
                logger.info(f"Reassigned {rows_updated} records and {matchup_updated} matchup entries (Total: {total_updated}) from source {from_source_id} to {to_source_id}.")
                return total_updated
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to reassign items: {e}")
                return 0

    @staticmethod
    def delete_source(source_id: int) -> bool:
        """
        Delete a source if it has no associated records or matchup queue entries.
        """
        with get_session() as session:
            # Explicit check for records
            record_count = session.query(Record).filter(Record.source_id == source_id).count()
            if record_count > 0:
                logger.warning(f"Cannot delete source {source_id}: it has {record_count} records.")
                return False
            
            # Explicit check for matchup queue entries
            matchup_count = session.query(MatchupQueue).filter(MatchupQueue.source_id == source_id).count()
            if matchup_count > 0:
                logger.warning(f"Cannot delete source {source_id}: it has {matchup_count} matchup queue entries.")
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
        """
        Retrieve a single record by ID with joined source and language info.
        """
        with get_session() as session:
            record = (
                session.query(Record)
                .filter(Record.id == record_id)
                .filter(Record.is_deleted == False)
                .first()
            )
            if not record:
                return None
            
            # Get languages
            languages = [
                {"id": lang.id, "code": lang.code, "name": lang.name}
                for lang in record.language
            ]
            
            return {
                "id": record.id,
                "lx": record.lx,
                "hm": record.hm,
                "ps": record.ps,
                "ge": record.ge,
                "source_id": record.source_id,
                "source_name": record.source.name if record.source else None,
                "source_page": record.source_page,
                "status": record.status,
                "mdf_data": record.mdf_data,
                "languages": languages,
                "updated_at": record.updated_at,
                "updated_by": record.updated_by,
                "reviewed_at": record.reviewed_at,
                "reviewed_by": record.reviewed_by,
                "current_version": record.current_version
            }

    @staticmethod
    def get_source(source_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single source by ID.
        """
        with get_session() as session:
            source = session.query(Source).filter(Source.id == source_id).first()
            if not source:
                return None
            
            return {
                "id": source.id,
                "name": source.name,
                "short_name": source.short_name,
                "description": source.description,
                "citation_format": source.citation_format,
                "created_at": source.created_at
            }

    @staticmethod
    def search_records(
        source_id: Optional[int] = None,
        language_id: Optional[int] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        search_mode: str = "Lexeme",
        record_ids: Optional[List[int]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> RecordSearchResult:
        """
        Search records with optional filters.
        Supports 'Lexeme' mode (via search_entries) and 'FTS' mode.
        If record_ids is provided, other filters are ignored except for is_deleted.
        """
        with get_session() as session:
            query = session.query(Record).filter(Record.is_deleted == False)
            
            if record_ids is not None:
                query = query.filter(Record.id.in_(record_ids))
            else:
                if source_id:
                    query = query.filter(Record.source_id == source_id)
                
                if language_id:
                    query = query.join(Record.language).filter(Language.id == language_id)
                
                if status:
                    query = query.filter(Record.status == status)
                
                if search_term:
                    if search_mode == "Lexeme":
                        # Join with search_entries to find matches in lx, va, se, etc.
                        query = query.join(Record.search_entries).filter(
                            SearchEntry.term.ilike(f"%{search_term}%")
                        ).distinct()
                    else:
                        # Native Full-Text Search (Roadmap Phase 6b)
                        # Supported by the pgserver envelope.
                        # Uses fts_vector column and GIN index via Migration 8
                        from sqlalchemy import text
                        
                        # Support for specific record ID search via #<id>
                        if search_term.startswith('#') and search_term[1:].isdigit():
                            query = query.filter(Record.id == int(search_term[1:]))
                        else:
                            query = query.filter(
                                text("records.fts_vector @@ plainto_tsquery('english', :term)")
                            ).params(term=search_term)
            
            # TODO: Sorting needs to be NFD with leading punctuation ignored.
            # Order by lx (headword)
            query = query.order_by(Record.lx, Record.hm)
            
            # Apply pagination
            total_count = query.count()
            results = query.offset(offset).limit(limit).all()
            
            records = []
            for r in results:
                records.append({
                    "id": r.id,
                    "lx": r.lx,
                    "hm": r.hm,
                    "ps": r.ps,
                    "ge": r.ge,
                    "status": r.status,
                    "source_id": r.source_id,
                    "source_name": r.source.name if r.source else None,
                    "mdf_data": r.mdf_data
                })
            
            return RecordSearchResult(
                records=records,
                total_count=total_count,
                limit=limit,
                offset=offset
            )

    @staticmethod
    def get_all_records_for_export(source_id: Optional[int] = None, search_term: Optional[str] = None, search_mode: str = "Lexeme", record_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all records matching the criteria for export, without pagination.
        """
        with get_session() as session:
            query = session.query(Record).filter(Record.is_deleted == False)
            
            if record_ids is not None:
                query = query.filter(Record.id.in_(record_ids))
            else:
                if source_id:
                    query = query.filter(Record.source_id == source_id)
                
                if search_term:
                    if search_mode == "Lexeme":
                        query = query.join(Record.search_entries).filter(
                            SearchEntry.term.ilike(f"%{search_term}%")
                        ).distinct()
                    else:
                        from sqlalchemy import text
                        if search_term.startswith('#') and search_term[1:].isdigit():
                            query = query.filter(Record.id == int(search_term[1:]))
                        else:
                            query = query.filter(
                                text("records.fts_vector @@ plainto_tsquery('english', :term)")
                            ).params(term=search_term)
            
            # TODO: Sorting needs to be NFD with leading punctuation ignored.
            # Order by source_id, lx (headword), hm
            query = query.order_by(Record.source_id, Record.lx, Record.hm)
            
            results = query.all()
            
            records = []
            for r in results:
                records.append({
                    "id": r.id,
                    "lx": r.lx,
                    "hm": r.hm,
                    "ps": r.ps,
                    "ge": r.ge,
                    "status": r.status,
                    "source_id": r.source_id,
                    "source_name": r.source.name if r.source else None,
                    "mdf_data": r.mdf_data
                })
            
            return records

    @staticmethod
    def bundle_records_to_mdf(records: List[Dict[str, Any]]) -> str:
        """
        Bundle a list of records into a single MDF text blob.
        Each record is separated by double blank lines.
        """
        # Ensure we have mdf_data and handle potential missing keys
        mdf_blocks = []
        for r in records:
            if 'mdf_data' in r:
                mdf_blocks.append(r['mdf_data'])
            elif 'id' in r:
                # Fallback to fetch if data is missing, though usually provided
                full_record = LinguisticService.get_record(r['id'])
                if full_record:
                    mdf_blocks.append(full_record['mdf_data'])
        
        return "\n\n".join(mdf_blocks)

    @staticmethod
    def create_record(**fields: Any) -> Optional[int]:
        """
        Create a new record.
        """
        with get_session() as session:
            try:
                record = Record(**fields)
                session.add(record)
                session.commit()
                session.refresh(record)
                logger.info(f"Created record {record.id}")
                return record.id
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to create record: {e}")
                return None

    @staticmethod
    def update_record(
        record_id: int, 
        user_email: str,
        session_id: Optional[str] = None,
        change_summary: Optional[str] = None,
        **fields: Any
    ) -> bool:
        """
        Update an existing record and record history.
        """
        from src.database.models.workflow import EditHistory
        
        with get_session() as session:
            record = session.query(Record).filter(Record.id == record_id).first()
            if not record:
                return False
            
            prev_data = record.mdf_data
            
            # Handle special status transition logic
            if fields.get('status') == 'approved' and record.status != 'approved':
                record.reviewed_at = func.now()
                record.reviewed_by = user_email
            
            # Update fields
            for key, value in fields.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            record.updated_by = user_email
            
            try:
                # Create history entry
                history = EditHistory(
                    record_id=record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=record.current_version + 1,
                    change_summary=change_summary or "Manual edit",
                    prev_data=prev_data,
                    current_data=record.mdf_data
                )
                session.add(history)
                
                # SQLAlchemy handles current_version increment via __mapper_args__ if configured,
                # but we'll manually ensure it if not automatically handled by the version_id_col.
                # Actually, core.py has version_id_col: current_version.
                
                session.commit()
                logger.info(f"Updated record {record_id} by {user_email}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update record {record_id}: {e}")
                return False

    @staticmethod
    def get_edit_history(record_id: int) -> List[Dict[str, Any]]:
        """
        Fetch revision history for a record.
        """
        from src.database.models.workflow import EditHistory
        with get_session() as session:
            history = session.query(EditHistory).filter(EditHistory.record_id == record_id).order_by(EditHistory.timestamp.desc()).all()
            return [
                {
                    "id": h.id,
                    "user_email": h.user_email,
                    "version": h.version,
                    "change_summary": h.change_summary,
                    "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S") if h.timestamp else "N/A"
                }
                for h in history
            ]

    @staticmethod
    def soft_delete_record(record_id: int, user_email: str) -> bool:
        """
        Soft-delete a record.
        """
        return LinguisticService.update_record(
            record_id=record_id,
            user_email=user_email,
            change_summary="Soft delete",
            is_deleted=True
        )

    @staticmethod
    def get_deleted_records() -> List[Dict[str, Any]]:
        """
        Fetch all soft-deleted records.
        """
        from src.database.models.identity import User
        with get_session() as session:
            # Join with User to get names if possible, but keep it simple
            records = session.query(Record).filter(Record.is_deleted == True).all()
            return [
                {
                    "id": r.id,
                    "lx": r.lx,
                    "deleted_by": r.updated_by,
                    "deleted_at": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else "N/A"
                }
                for r in records
            ]

    @staticmethod
    def hard_delete_record(record_id: int) -> bool:
        """
        Permanently delete a record and its history.
        """
        from src.database.models.workflow import EditHistory, MatchupQueue
        from src.database.models.search import SearchEntry
        with get_session() as session:
            try:
                # 1. Delete history first
                session.query(EditHistory).filter(EditHistory.record_id == record_id).delete()
                
                # 2. Delete search entries
                session.query(SearchEntry).filter(SearchEntry.record_id == record_id).delete()
                
                # 3. Handle matchup queue suggestions (set to NULL or delete?)
                # Since this is a hard delete of the record, we should NULL the suggestion
                # so the entry remains in the queue but is no longer linked to a non-existent record.
                session.query(MatchupQueue).filter(MatchupQueue.suggested_record_id == record_id).update({"suggested_record_id": None})
                
                # 4. Delete record (CASCADE handles record_languages)
                session.query(Record).filter(Record.id == record_id).delete()
                
                session.commit()
                logger.info(f"Hard deleted record {record_id}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to hard delete record {record_id}: {e}")
                return False

    @staticmethod
    def restore_record(record_id: int, user_email: str) -> bool:
        """
        Restore a soft-deleted record.
        """
        return LinguisticService.update_record(
            record_id=record_id,
            user_email=user_email,
            change_summary="Restored",
            is_deleted=False
        )
