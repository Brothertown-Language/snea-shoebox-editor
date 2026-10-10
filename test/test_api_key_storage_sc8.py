# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Key-storage discipline tests — issue #1420, SC-8.

Secrets exist only as PBKDF2 hashes at rest: after issuing keys, a database
inspection finds no plaintext secret value and finds the versioned
``pbkdf2_sha256$`` hash format for every key; the known secret still
authenticates (hash correctness).

Runs against the prod-synced local database per the regression protocol.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import re
import unittest

from sqlalchemy import text

from src.database.models.api_keys import ApiKeys
from src.services.api_key_service import ApiKeyService

_HASH_FORMAT = re.compile(r"^pbkdf2_sha256\$\d+\$[A-Za-z0-9+/=]+\$[A-Za-z0-9+/=]+$")
_LABEL_PREFIX = "sc8-selftest"


class ApiKeyStorageTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.database.connection import init_db

        init_db()  # applies migration 2026100979333 if pending → api_keys exists

    def tearDown(self):
        # Remove rows created by this test suite (keep the table tidy; the
        # audit log intentionally retains its entries).
        from src.database.connection import get_session

        if not self.created_keys:
            return
        session = get_session()
        try:
            session.query(ApiKeys).filter(ApiKeys.key.in_(self.created_keys)).delete(synchronize_session=False)
            session.commit()
        finally:
            session.close()
        self.created_keys = []

    def test_create_stores_only_versioned_hash(self):
        key, secret = ApiKeyService.create_key(f"{_LABEL_PREFIX}-1", "sc8-test-admin")
        self.created_keys.append(key)

        from src.database.connection import get_session

        session = get_session()
        try:
            rows = session.execute(text("SELECT * FROM api_keys")).mappings().all()
        finally:
            session.close()

        # Full-table scan: the plaintext secret appears NOWHERE.
        for row in rows:
            serialized = " ".join(str(v) for v in row.values() if v is not None)
            self.assertNotIn(secret, serialized, "plaintext secret found at rest")
            if row["key"] == key:
                self.assertRegex(row["secret_hash"], _HASH_FORMAT)

        # Exactly one row for the issued key.
        matched = [r for r in rows if r["key"] == key]
        self.assertEqual(len(matched), 1)

    def test_issued_secret_authenticates_hash_correctness(self):
        key, secret = ApiKeyService.create_key(f"{_LABEL_PREFIX}-2", "sc8-test-admin")
        self.created_keys.append(key)
        status, row = ApiKeyService.authenticate(key, secret)
        self.assertEqual(status, "ok")
        self.assertIsNotNone(row)
        # last_used_at updated on success (R-6)
        self.assertIsNotNone(row.last_used_at)

    def test_wrong_secret_fails_closed(self):
        key, secret = ApiKeyService.create_key(f"{_LABEL_PREFIX}-3", "sc8-test-admin")
        self.created_keys.append(key)
        wrong_secret = secret[:-1] + ("A" if secret[-1] != "A" else "B")
        status, _row = ApiKeyService.authenticate(key, wrong_secret)
        self.assertEqual(status, "invalid")
        status2, _row2 = ApiKeyService.authenticate("snea_unknown_key_value", secret)
        self.assertEqual(status2, "invalid")


if __name__ == "__main__":
    unittest.main()
