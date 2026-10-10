# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Rate-limit live burst test — issue #1420, SC-10 (E2E pass).

Requires the app to be running with a LOW ``api.rate_limit_per_minute``
secrets value (the harness documents 3). Bursts one key past the window:
429 + Retry-After on every request past the window, a second key's
concurrent requests return 200, and the request count that triggers the
first 429 equals the configured limit.

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
CONFIGURED_LIMIT = int(os.environ.get("SNEA_E2E_RATE_LIMIT", "3"))


def _app_healthy() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _get(key: str, secret: str):
    req = urllib.request.Request(ENDPOINT, headers={"X-API-Key": key, "X-API-Secret": secret})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


@unittest.skipIf(pytestmark_skip, "live-app burst test — run with SNEA_E2E=1, low rate limit, app up")
class LiveBurstTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        if not _app_healthy():
            raise unittest.SkipTest("live app not healthy on " + BASE)
        from src.database.connection import init_db
        from src.services.api_key_service import ApiKeyService

        init_db()
        cls.key_a, cls.secret_a = ApiKeyService.create_key("sc10-burst-a", "sc10-test-admin")
        cls.created_keys.append(cls.key_a)
        cls.key_b, cls.secret_b = ApiKeyService.create_key("sc10-burst-b", "sc10-test-admin")
        cls.created_keys.append(cls.key_b)

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

    def test_burst_past_window_429_with_retry_after_and_second_key_ok(self):
        statuses = []
        first_429_index = None
        retry_after_values = []
        first_429_body = None
        for i in range(CONFIGURED_LIMIT + 3):
            status, headers, body = _get(self.key_a, self.secret_a)
            statuses.append(status)
            if status == 429:
                retry_after_values.append(headers.get("Retry-After"))
                if first_429_index is None:
                    first_429_index = i
                    first_429_body = body

        self.assertIsNotNone(first_429_index, "bursting past the window must produce a 429")
        self.assertEqual(
            first_429_index,
            CONFIGURED_LIMIT,
            f"the first 429 must be request #{CONFIGURED_LIMIT + 1} (0-based {CONFIGURED_LIMIT})",
        )
        self.assertTrue(all(s == 429 for s in statuses[CONFIGURED_LIMIT:]), "every request past the window must be 429")
        self.assertTrue(
            all(v is not None and int(v) > 0 for v in retry_after_values),
            "429 must carry a positive Retry-After",
        )

        # SC-12 live spot-check: the 429 body is the generic JSON error shape.
        body_429 = json.loads(first_429_body.decode("utf-8"))
        self.assertEqual(body_429, {"error": {"code": "rate_limited", "message": "Rate limit exceeded."}})

        # A second key's concurrent requests still succeed.
        status_b, _headers_b, _body_b = _get(self.key_b, self.secret_b)
        self.assertEqual(status_b, 200, "a second key must not be throttled by the first key's burst")


if __name__ == "__main__":
    unittest.main()
