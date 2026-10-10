# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""No-DB-exposure tests — issue #1420, SC-12.

Every error response body for every status code contains only the generic
JSON error shape — no connection strings, hosts, ports, SQL, or stack
traces. Unit-asserts every error formatter's output against a blocklist
pattern set; live spot-checks of 401/404 bodies.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import re
import unittest
import urllib.error
import urllib.request

from src.api.errors import MESSAGES, error_body

BASE = os.environ.get("SNEA_E2E_BASE_URL", "http://localhost:8501")

# Blocklist: infrastructure details that must never appear in error output
BLOCKLIST = [
    re.compile(r"postgres(ql)?://", re.IGNORECASE),
    re.compile(r"postgresql", re.IGNORECASE),
    re.compile(r"localhost:\d+"),
    re.compile(r"127\.0\.0\.1"),
    re.compile(r"0\.0\.0\.0"),
    re.compile(r"host=|port=", re.IGNORECASE),
    re.compile(r"\bSELECT\b.+\bFROM\b", re.IGNORECASE),
    re.compile(r"\bINSERT\b.+\bINTO\b", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"File \"", re.IGNORECASE),
    re.compile(r"\.py\b", re.IGNORECASE),
    re.compile(r"sqlalchemy", re.IGNORECASE),
    re.compile(r"connection string", re.IGNORECASE),
    re.compile(r"psycopg", re.IGNORECASE),
]


def _live_app_up() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


class ErrorFormatterExposureTests(unittest.TestCase):
    def test_every_status_has_the_generic_shape(self):
        for status in (401, 403, 404, 405, 429, 503):
            body = json.loads(error_body(status))
            self.assertEqual(set(body.keys()), {"error"})
            self.assertEqual(set(body["error"].keys()), {"code", "message"})
            self.assertEqual(body["error"]["code"], MESSAGES[status][0])

    def test_no_formatter_output_contains_blocklisted_content(self):
        for status in (401, 403, 404, 405, 429, 503):
            text = error_body(status).decode("utf-8")
            for pattern in BLOCKLIST:
                self.assertIsNone(
                    pattern.search(text),
                    f"status {status}: error body leaks infrastructure detail matching {pattern.pattern!r}",
                )

    def test_messages_are_static_across_calls(self):
        for status in MESSAGES:
            self.assertEqual(error_body(status), error_body(status), "messages must be static")


@unittest.skipIf(os.environ.get("SNEA_E2E", "") != "1" or not _live_app_up(), "live spot-checks need the app up")
class LiveErrorSpotChecks(unittest.TestCase):
    def test_401_body_is_generic(self):
        try:
            urllib.request.urlopen(BASE + "/api/v1/records", timeout=10)
            self.fail("expected 401")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8")
            body = json.loads(text)
            self.assertEqual(body["error"]["code"], "unauthorized")
            for pattern in BLOCKLIST:
                self.assertIsNone(pattern.search(text), f"401 body leaks {pattern.pattern!r}")

    def test_404_body_is_generic(self):
        try:
            urllib.request.urlopen(BASE + "/api/nope", timeout=10)
            self.fail("expected 404")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8")
            body = json.loads(text)
            self.assertEqual(body["error"]["code"], "not_found")
            for pattern in BLOCKLIST:
                self.assertIsNone(pattern.search(text), f"404 body leaks {pattern.pattern!r}")


if __name__ == "__main__":
    unittest.main()
