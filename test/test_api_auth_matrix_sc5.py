# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Auth + method matrix tests — issue #1420, SC-5.

HTTP-level suite against the live app with seeded keys covering the full
matrix: valid pair → 200; unknown key → 401; wrong secret → 401 (uniform
message); disabled key → 403; revoked key → 403; missing headers → 401;
POST → 405; unknown /api/ path → JSON 404.

Skips unless SNEA_E2E=1 with the live app healthy (the bolt requires a
first browser session; run the Playwright warmup before this suite).

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

LABEL_PREFIX = "sc5-matrix"


def _app_healthy() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _request(method: str, url: str, headers: dict | None = None, data: bytes | None = None):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


@unittest.skipIf(pytestmark_skip, "live-app HTTP suite — run with SNEA_E2E=1 and the app up")
class AuthMatrixTests(unittest.TestCase):
    created_keys: list[str] = []

    @classmethod
    def setUpClass(cls):  # noqa: N802
        if not _app_healthy():
            raise unittest.SkipTest("live app not healthy on " + BASE)
        from src.database.connection import init_db
        from src.services.api_key_service import ApiKeyService

        init_db()
        cls.valid_key, cls.valid_secret = ApiKeyService.create_key(f"{LABEL_PREFIX}-valid", "sc5-test-admin")
        cls.created_keys.append(cls.valid_key)
        cls.disabled_key, cls.disabled_secret = ApiKeyService.create_key(f"{LABEL_PREFIX}-disabled", "sc5-test-admin")
        cls.created_keys.append(cls.disabled_key)
        ApiKeyService.set_enabled(cls.disabled_key, False, "sc5-test-admin")
        cls.revoked_key, cls.revoked_secret = ApiKeyService.create_key(f"{LABEL_PREFIX}-revoked", "sc5-test-admin")
        cls.created_keys.append(cls.revoked_key)
        ApiKeyService.revoke_key(cls.revoked_key, "sc5-test-admin")

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

    def _get(self, key: str | None, secret: str | None):
        headers = {}
        if key is not None:
            headers["X-API-Key"] = key
        if secret is not None:
            headers["X-API-Secret"] = secret
        return _request("GET", ENDPOINT, headers=headers)

    def test_valid_pair_returns_200(self):
        status, headers, body = self._get(self.valid_key, self.valid_secret)
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        payload = json.loads(body)
        self.assertIn("count", payload)
        self.assertIn("records", payload)

    def test_unknown_key_401(self):
        status, headers, body = self._get("snea_totally_unknown_key", "whatever-secret")
        self.assertEqual(status, 401)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertEqual(json.loads(body), {"error": {"code": "unauthorized", "message": "Authentication required."}})

    def test_wrong_secret_401_uniform_message(self):
        status, _h, body = self._get(self.valid_key, "definitely-the-wrong-secret")
        self.assertEqual(status, 401)
        unknown = json.loads(self._get("snea_totally_unknown_key", "x")[2])
        wrong = json.loads(body)
        self.assertEqual(unknown, wrong, "401 must not distinguish unknown key from bad secret")

    def test_disabled_key_403(self):
        status, _h, body = self._get(self.disabled_key, self.disabled_secret)
        self.assertEqual(status, 403)
        self.assertEqual(
            json.loads(body), {"error": {"code": "key_disabled", "message": "API key is disabled or revoked."}}
        )

    def test_revoked_key_403(self):
        status, _h, body = self._get(self.revoked_key, self.revoked_secret)
        self.assertEqual(status, 403)
        self.assertEqual(json.loads(body)["error"]["code"], "key_disabled")

    def test_missing_headers_401(self):
        for headers in ({}, {"X-API-Key": self.valid_key}, {"X-API-Secret": self.valid_secret}):
            status, _h, body = _request("GET", ENDPOINT, headers=headers)
            self.assertEqual(status, 401, f"headers={headers}")
            self.assertEqual(json.loads(body)["error"]["code"], "unauthorized")

    def test_empty_header_values_fail_as_missing(self):
        status, _h, body = self._get("", "")
        self.assertEqual(status, 401)
        self.assertEqual(json.loads(body)["error"]["code"], "unauthorized")

    def test_post_is_405_json(self):
        status, headers, body = _request("POST", ENDPOINT, data=b"{}")
        self.assertEqual(status, 405)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertEqual(json.loads(body), {"error": {"code": "method_not_allowed", "message": "Method not allowed."}})

    def test_unknown_api_path_is_json_404(self):
        status, headers, body = _request("GET", BASE + "/api/v2/other")
        self.assertEqual(status, 404)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        self.assertEqual(json.loads(body), {"error": {"code": "not_found", "message": "Unknown API endpoint."}})

    def test_query_parameters_are_ignored(self):
        status, _h, body = self._get(self.valid_key, self.valid_secret)
        self.assertEqual(status, 200)
        status2, _h2, _body2 = _request(
            "GET",
            ENDPOINT + "?unexpected=param",
            headers={"X-API-Key": self.valid_key, "X-API-Secret": self.valid_secret},
        )
        self.assertEqual(status2, 200)
        self.assertEqual(len(json.loads(body)["records"]), len(json.loads(_body2)["records"]))


if __name__ == "__main__":
    unittest.main()
