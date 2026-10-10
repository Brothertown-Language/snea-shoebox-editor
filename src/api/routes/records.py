# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""``GET /api/v1/records`` — full dump of live linguistic records (#1420).

Serves the live (``is_deleted = false``) rows of the ``records`` table as a
single JSON document, ordered by ascending ``id``. Each record is serialized
against a CLOSED 15-field whitelist (spec Interface Contract); the resolved
source name and primary-first language codes are embedded so each record is
self-contained. Excluded by design: ``embedding``, lock state, and internal
user-identity columns.

Response encoding (R-10): ``application/json; charset=utf-8`` with
``ensure_ascii=False`` — linguistic content (ə, ŋ, ã, č, ꝏ, combining
diacritics) is preserved byte-exact from the database, never normalized.
"""

from __future__ import annotations

from src.logging_config import get_logger

from ..auth import require_credentials
from ..context import get_session_factory
from ..errors import send_error_json
from . import BaseAPIHandler

logger = get_logger("src.api.routes.records")

PATH = "/api/v1/records"


def _serialize_record(record, source_name: str, language_codes: list[str]) -> dict:
    """Project a Record row onto the closed field whitelist."""
    return {
        "id": record.id,
        "lx": record.lx,
        "sort_lx": record.sort_lx,
        "hm": record.hm,
        "ps": record.ps,
        "ge": record.ge,
        "source_id": record.source_id,
        "source_page": record.source_page,
        "status": record.status,
        "mdf_data": record.mdf_data,
        "current_version": record.current_version,
        "is_deleted": record.is_deleted,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "source": source_name,
        "languages": language_codes,
    }


class RecordsHandler(BaseAPIHandler):
    def get(self) -> None:
        if not require_credentials(self):
            return

        factory = get_session_factory()
        if factory is None:
            logger.error("No session factory captured at bolt time; failing closed")
            send_error_json(self, 503)
            return

        try:
            from sqlalchemy.orm import joinedload

            from src.database.models.core import Language, Record, RecordLanguage

            session = factory()
            try:
                records = (
                    session.query(Record)
                    .options(joinedload(Record.source))
                    .filter(Record.is_deleted.is_(False))
                    .order_by(Record.id.asc())
                    .all()
                )
                # Language codes per record, primary first, remaining by join-row id.
                join_rows = (
                    session.query(RecordLanguage.record_id, Language.code, RecordLanguage.is_primary)
                    .join(Language, RecordLanguage.language_id == Language.id)
                    .order_by(RecordLanguage.id.asc())
                    .all()
                )
            finally:
                session.close()

            languages_by_record: dict[int, list[str]] = {}
            for record_id, code, is_primary in join_rows:
                codes = languages_by_record.setdefault(record_id, [])
                if is_primary:
                    codes.insert(0, code)
                else:
                    codes.append(code)

            payload_records = [
                _serialize_record(
                    record,
                    record.source.name if record.source is not None else None,
                    languages_by_record.get(record.id, []),
                )
                for record in records
            ]
        except Exception:
            logger.error("Records dump query failed; failing closed", exc_info=True)
            send_error_json(self, 503)
            return

        self.send_json({"count": len(payload_records), "records": payload_records})


HANDLER = RecordsHandler
