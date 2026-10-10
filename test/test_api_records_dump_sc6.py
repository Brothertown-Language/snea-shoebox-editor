# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Dump payload fidelity tests — issue #1420, SC-6.

The dump payload matches the database exactly: count equals the live-record
count, every record matches the DB row on every whitelisted field, ordering
is by ascending id, and no excluded column appears.

Skips unless SNEA_E2E=1 with the live app healthy.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import unittest
import urllib.error
import urllib.request

pytestmark_skip = os.environ.get("SNEA_E2E", "") != "1"

BASE = os.environ.get("SNEA_E2E_BASE_URL", "http://localhost:8501")
ENDPOINT = BASE + "/api/v1/records"

# Closed 15-field whitelist (spec Interface Contract)
WHITELIST = {
    "id",
    "lx",
    "sort_lx",
    "hm",
    "ps",
    "ge",
    "source_id",
    "source_page",
    "status",
    "mdf_data",
    "current_version",
    "is_deleted",
    "updated_at",
    "source",
    "languages",
}
# Excluded by design — must never appear
EXCLUDED = {"embedding", "is_locked", "locked_by", "locked_at", "lock_note", "updated_by", "reviewed_by", "reviewed_at"}


def _app_healthy() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


@unittest.skipIf(pytestmark_skip, "live-app HTTP suite — run with SNEA_E2E=1 and the app up")
class DumpPayloadTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        if not _app_healthy():
            raise unittest.SkipTest("live app not healthy on " + BASE)
        from src.database.connection import init_db
        from src.services.api_key_service import ApiKeyService

        init_db()
        cls.key, cls.secret = ApiKeyService.create_key("sc6-dump", "sc6-test-admin")
        cls.created_keys.append(cls.key)
        req = urllib.request.Request(ENDPOINT, headers={"X-API-Key": cls.key, "X-API-Secret": cls.secret})
        with urllib.request.urlopen(req, timeout=120) as r:
            cls.payload = json.loads(r.read().decode("utf-8"))

    @classmethod
    def tearDownClass(cls):  # noqa: N802
        from src.database.connection import get_session
        from src.database.models.api_keys import ApiKeys

        session = get_session()
        try:
            session.query(ApiKeys).filter(ApiKeys.key.in_(cls.created_keys)).delete(synchronize_session=False)
            session.commit()
        finally:
            session.close()

    def test_count_equals_live_record_count(self):
        from src.database.connection import get_session
        from src.database.models.core import Record

        session = get_session()
        try:
            live_count = session.query(Record).filter(Record.is_deleted.is_(False)).count()
        finally:
            session.close()
        self.assertEqual(self.payload["count"], live_count)
        self.assertEqual(len(self.payload["records"]), live_count)

    def test_ordering_is_ascending_id(self):
        ids = [r["id"] for r in self.payload["records"]]
        self.assertEqual(ids, sorted(ids))

    def test_every_record_matches_db_on_every_whitelisted_field(self):
        from src.database.connection import get_session
        from src.database.models.core import Language, Record, RecordLanguage, Source

        session = get_session()
        try:
            db_records = {r.id: r for r in session.query(Record).filter(Record.is_deleted.is_(False)).all()}
            sources = {s.id: s.name for s in session.query(Source).all()}
            join_rows = (
                session.query(RecordLanguage.record_id, Language.code, RecordLanguage.is_primary)
                .join(Language, RecordLanguage.language_id == Language.id)
                .order_by(RecordLanguage.id.asc())
                .all()
            )
        finally:
            session.close()
        langs: dict[int, list[str]] = {}
        for record_id, code, is_primary in join_rows:
            codes = langs.setdefault(record_id, [])
            if is_primary:
                codes.insert(0, code)
            else:
                codes.append(code)

        for entry in self.payload["records"]:
            record = db_records[entry["id"]]
            self.assertEqual(set(entry.keys()), WHITELIST, f"field set mismatch on id={entry['id']}")
            self.assertEqual(entry["lx"], record.lx)
            self.assertEqual(entry["sort_lx"], record.sort_lx)
            self.assertEqual(entry["hm"], record.hm)
            self.assertEqual(entry["ps"], record.ps)
            self.assertEqual(entry["ge"], record.ge)
            self.assertEqual(entry["source_id"], record.source_id)
            self.assertEqual(entry["source_page"], record.source_page)
            self.assertEqual(entry["status"], record.status)
            self.assertEqual(entry["mdf_data"], record.mdf_data)
            self.assertEqual(entry["current_version"], record.current_version)
            self.assertEqual(entry["is_deleted"], record.is_deleted)
            self.assertEqual(entry["updated_at"], record.updated_at.isoformat() if record.updated_at else None)
            self.assertEqual(entry["source"], sources.get(record.source_id))
            self.assertEqual(entry["languages"], langs.get(record.id, []))

    def test_no_soft_deleted_records_served(self):
        served_ids = {r["id"] for r in self.payload["records"]}
        from src.database.connection import get_session
        from src.database.models.core import Record

        session = get_session()
        try:
            deleted_ids = {r.id for r in session.query(Record.id).filter(Record.is_deleted.is_(True))}
        finally:
            session.close()
        self.assertFalse(served_ids & deleted_ids, "soft-deleted records must never be served")


if __name__ == "__main__":
    unittest.main()
