# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Key lifecycle audit-trail tests — issue #1420, SC-9 (lifecycle events).

Create/regenerate/enable/disable/revoke events appear in
``system_event_log`` with the specified event types, key identifiers, and
NO secret material. (Auth-failure events are exercised at the API layer in
Phase 4.)

Runs against the prod-synced local database per the regression protocol.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import os
import unittest
import urllib.error
import urllib.request

from sqlalchemy import text

from src.database.models.api_keys import ApiKeys
from src.services.api_key_service import ApiKeyService

BASE = os.environ.get("SNEA_E2E_BASE_URL", "http://localhost:8501")


class ApiKeyAuditTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.database.connection import init_db

        init_db()

    def tearDown(self):
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

    def _events_for(self, key: str, event_type: str | None = None) -> list:
        from src.database.connection import get_session

        session = get_session()
        try:
            query = session.execute(
                text(
                    "SELECT event_type, message, details FROM system_event_log "
                    "WHERE source = 'src.services.api_key_service' "
                    "AND message LIKE :pattern ORDER BY id DESC"
                ),
                {"pattern": f"%{key}%"},
            )
            rows = query.mappings().all()
        finally:
            session.close()
        if event_type is not None:
            rows = [r for r in rows if r["event_type"] == event_type]
        return rows

    def test_full_lifecycle_audits_each_event_without_secret_material(self):
        key, secret = ApiKeyService.create_key("sc9-selftest", "sc9-test-admin")
        self.created_keys.append(key)

        new_secret = ApiKeyService.regenerate_secret(key, "sc9-test-admin")
        self.assertIsNotNone(new_secret)

        self.assertTrue(ApiKeyService.set_enabled(key, False, "sc9-test-admin"))
        self.assertTrue(ApiKeyService.set_enabled(key, True, "sc9-test-admin"))
        self.assertTrue(ApiKeyService.revoke_key(key, "sc9-test-admin"))

        expected = {
            "api_key_created": 1,
            "api_key_regenerated": 1,
            "api_key_disabled": 1,
            "api_key_enabled": 1,
            "api_key_revoked": 1,
        }
        for event_type, minimum in expected.items():
            rows = self._events_for(key, event_type)
            self.assertGreaterEqual(len(rows), minimum, f"missing {event_type} event for {key}")

        # Acting admin identified; no secret material in ANY event row
        # (neither the original nor the regenerated secret).
        rows = self._events_for(key)
        self.assertGreaterEqual(len(rows), 5)
        for row in rows:
            blob = f"{row['message']} {row['details']}"
            self.assertNotIn(secret, blob, "original secret leaked into audit")
            self.assertNotIn(new_secret, blob, "regenerated secret leaked into audit")
            self.assertIn("sc9-test-admin", blob)

    def test_regenerated_secret_invalidates_old_immediately(self):
        key, old_secret = ApiKeyService.create_key("sc9-selftest-rotate", "sc9-test-admin")
        self.created_keys.append(key)
        status1, _ = ApiKeyService.authenticate(key, old_secret)
        self.assertEqual(status1, "ok")

        new_secret = ApiKeyService.regenerate_secret(key, "sc9-test-admin")
        self.assertNotEqual(new_secret, old_secret)

        status_old, _ = ApiKeyService.authenticate(key, old_secret)
        self.assertEqual(status_old, "invalid", "old secret must be invalid immediately")
        status_new, _ = ApiKeyService.authenticate(key, new_secret)
        self.assertEqual(status_new, "ok")

    def test_revoked_key_authenticates_as_inactive(self):
        key, secret = ApiKeyService.create_key("sc9-selftest-revoke", "sc9-test-admin")
        self.created_keys.append(key)
        self.assertTrue(ApiKeyService.revoke_key(key, "sc9-test-admin"))
        status, row = ApiKeyService.authenticate(key, secret)
        self.assertEqual(status, "inactive")
        # Rows are retained for audit — the row still exists.
        self.assertIsNotNone(row)

    def test_disabled_key_authenticates_as_inactive(self):
        key, secret = ApiKeyService.create_key("sc9-selftest-disable", "sc9-test-admin")
        self.created_keys.append(key)
        self.assertTrue(ApiKeyService.set_enabled(key, False, "sc9-test-admin"))
        status, row = ApiKeyService.authenticate(key, secret)
        self.assertEqual(status, "inactive")
        self.assertIsNotNone(row)


def _app_healthy() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


@unittest.skipIf(os.environ.get("SNEA_E2E", "") != "1" or not _app_healthy(), "auth-failure events need the live app")
class AuthFailureAuditTests(unittest.TestCase):
    """SC-9 (auth failures): every failed attempt (401 and 403) appears in
    system_event_log as api_auth_failure with the presented key identifier
    and outcome — never the presented secret."""

    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        from src.database.connection import init_db
        from src.services.api_key_service import ApiKeyService

        init_db()
        cls.disabled_key, cls.disabled_secret = ApiKeyService.create_key("sc9-authfail-disabled", "sc9-test-admin")
        cls.created_keys.append(cls.disabled_key)
        ApiKeyService.set_enabled(cls.disabled_key, False, "sc9-test-admin")

    @classmethod
    def tearDownClass(cls):  # noqa: N802
        from src.database.connection import get_session

        if not cls.created_keys:
            return
        session = get_session()
        try:
            session.query(ApiKeys).filter(ApiKeys.key.in_(cls.created_keys)).delete(synchronize_session=False)
            session.commit()
        finally:
            session.close()

    def _failures_for(self, key: str) -> list:
        from src.database.connection import get_session

        session = get_session()
        try:
            rows = (
                session.execute(
                    text(
                        "SELECT message, details FROM system_event_log "
                        "WHERE event_type = 'api_auth_failure' AND details->>'presented_key' = :key "
                        "ORDER BY id DESC"
                    ),
                    {"key": key},
                )
                .mappings()
                .all()
            )
        finally:
            session.close()
        return rows

    def test_unknown_key_failure_audited_without_secret(self):
        secret = "sc9-never-logged-secret-value"
        req = urllib.request.Request(
            BASE + "/api/v1/records",
            headers={"X-API-Key": "snea_sc9_unknown_probe", "X-API-Secret": secret},
        )
        try:
            urllib.request.urlopen(req, timeout=30)
            self.fail("expected 401")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)

        rows = self._failures_for("snea_sc9_unknown_probe")
        self.assertGreaterEqual(len(rows), 1, "the failed attempt must be audited")
        blob = f"{rows[0]['message']} {rows[0]['details']}"
        self.assertNotIn(secret, blob, "the presented secret must never enter the audit trail")
        self.assertIn("invalid_credentials", blob)

    def test_disabled_key_failure_audited(self):
        req = urllib.request.Request(
            BASE + "/api/v1/records",
            headers={"X-API-Key": self.disabled_key, "X-API-Secret": self.disabled_secret},
        )
        try:
            urllib.request.urlopen(req, timeout=30)
            self.fail("expected 403")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 403)

        rows = self._failures_for(self.disabled_key)
        self.assertGreaterEqual(len(rows), 1, "the 403 outcome must be audited")
        self.assertIn("key_inactive", f"{rows[0]['message']} {rows[0]['details']}")


if __name__ == "__main__":
    unittest.main()
