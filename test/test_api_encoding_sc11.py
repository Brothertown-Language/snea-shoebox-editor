# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Response encoding tests — issue #1420, SC-11.

UTF-8 JSON with unescaped Unicode: Content-Type is
``application/json; charset=utf-8``, Unicode-bearing headwords/glosses
appear as raw UTF-8 (no ``\\u`` escapes), and linguistic content is
byte-identical to the database.

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

# Characters that must appear RAW in the response bytes when present in data
IPA_MARKERS = ["ə", "ŋ", "ã", "č", "ꝏ", "ô", "8", "·"]


def _app_healthy() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


@unittest.skipIf(pytestmark_skip, "live-app HTTP suite — run with SNEA_E2E=1 and the app up")
class EncodingTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        if not _app_healthy():
            raise unittest.SkipTest("live app not healthy on " + BASE)
        from src.database.connection import init_db
        from src.services.api_key_service import ApiKeyService

        init_db()
        cls.key, cls.secret = ApiKeyService.create_key("sc11-encoding", "sc11-test-admin")
        cls.created_keys.append(cls.key)
        req = urllib.request.Request(ENDPOINT, headers={"X-API-Key": cls.key, "X-API-Secret": cls.secret})
        with urllib.request.urlopen(req, timeout=120) as r:
            cls.content_type = r.headers.get("Content-Type", "")
            cls.raw_bytes = r.read()

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

    def test_content_type_is_utf8_json(self):
        self.assertEqual(self.content_type, "application/json; charset=utf-8")

    def test_unicode_not_escaped_in_raw_bytes(self):
        raw = self.raw_bytes
        self.assertNotIn(b"\\u", raw, "response must not contain \\u escapes")
        # The response must decode strictly as UTF-8.
        text = raw.decode("utf-8")
        # At least some linguistic markers must be present in the corpus dump.
        found = [c for c in IPA_MARKERS if c in text]
        self.assertTrue(found, f"no Unicode linguistic markers found in dump (tried {IPA_MARKERS})")

    def test_unicode_fields_byte_identical_to_database(self):
        payload = json.loads(self.raw_bytes.decode("utf-8"))
        from src.database.connection import get_session
        from src.database.models.core import Record

        session = get_session()
        try:
            # Records whose headword carries non-ASCII characters.
            candidates = (
                session.query(Record)
                .filter(Record.lx.op("~")("[^\\x00-\\x7F]"))
                .filter(Record.is_deleted.is_(False))
                .order_by(Record.id.asc())
                .limit(200)
                .all()
            )
        finally:
            session.close()
        self.assertGreater(len(candidates), 0, "database should contain non-ASCII headwords")
        served = {r["id"]: r for r in payload["records"]}
        for record in candidates:
            entry = served[record.id]
            self.assertEqual(entry["lx"], record.lx, f"id={record.id}: lx byte mismatch")
            self.assertNotEqual(
                record.lx.encode("ascii", "ignore").decode(), record.lx or "", "sanity: candidate is non-ascii"
            )
            # The exact characters survive the round trip.
            self.assertEqual(entry["lx"].encode("utf-8"), (record.lx or "").encode("utf-8"))

    def test_linguistic_content_not_normalized(self):
        """Combining diacritics and special letters survive unnormalized."""
        payload = json.loads(self.raw_bytes.decode("utf-8"))
        from src.database.connection import get_session
        from src.database.models.core import Record

        session = get_session()
        try:
            sample = (
                session.query(Record.id, Record.mdf_data)
                .filter(Record.mdf_data.op("~")("[^\\x00-\\x7F]"))
                .filter(Record.is_deleted.is_(False))
                .limit(50)
                .all()
            )
        finally:
            session.close()
        served = {r["id"]: r for r in payload["records"]}
        for record_id, mdf in sample:
            self.assertEqual(served[record_id]["mdf_data"], mdf, f"id={record_id}: mdf_data mismatch")


if __name__ == "__main__":
    unittest.main()
