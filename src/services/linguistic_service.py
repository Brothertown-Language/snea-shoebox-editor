# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Linguistic Service scaffold for future CRUD operations on Record, Source, and Language models.

Note: This is a scaffold only. Full implementation should be deferred until the frontend pages
(view_record.py, view_source.py) are built out and actual data-access patterns are established.
"""
from typing import Optional, List, Dict, Any


class LinguisticService:
    """
    Service for centralizing data access to linguistic models (Record, Source, Language).
    Stub methods define the intended interface for future CRUD implementation.
    """

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
