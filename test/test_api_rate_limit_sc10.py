# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Rate-limit unit tests — issue #1420, SC-10 (limiter semantics).

Fixed-window semantics in-process: the enforced limit matches the
configured value, a second key is unaffected, Retry-After is positive and
bounded by the window. (The live burst assertion runs in the E2E pass.)

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import unittest

from src.api.auth import _WINDOW_SECONDS, limiter
from src.api.context import set_rate_limit


class RateLimiterSemanticsTests(unittest.TestCase):
    def setUp(self):
        set_rate_limit(3)
        limiter._windows.clear()

    def tearDown(self):
        set_rate_limit(None)  # restore default
        limiter._windows.clear()

    def test_requests_up_to_limit_pass_then_429(self):
        outcomes = [limiter.check("key-a") for _ in range(5)]
        self.assertEqual(outcomes[:3], [None, None, None], "requests within the limit must pass")
        self.assertTrue(all(o is not None for o in outcomes[3:]), "requests past the limit must be limited")

    def test_second_key_unaffected(self):
        for _ in range(3):
            limiter.check("key-a")
        self.assertIsNotNone(limiter.check("key-a"))
        self.assertIsNone(limiter.check("key-b"), "a second key must not be throttled by the first")

    def test_retry_after_within_window(self):
        limiter.check("key-a")
        limiter.check("key-a")
        limiter.check("key-a")
        retry_after = limiter.check("key-a")
        self.assertIsNotNone(retry_after)
        self.assertGreater(retry_after, 0)
        self.assertLessEqual(retry_after, _WINDOW_SECONDS + 1)

    def test_window_resets(self):
        # Simulate an expired window by rewinding the stored window start.
        limiter.check("key-a")
        limiter.check("key-a")
        limiter.check("key-a")
        start, _count = limiter._windows["key-a"]
        limiter._windows["key-a"] = (start - _WINDOW_SECONDS * 2, 3)
        self.assertIsNone(limiter.check("key-a"), "a new window must allow requests again")

    def test_zero_or_invalid_config_falls_back_to_default(self):
        set_rate_limit(0)
        self.assertEqual(60, __import__("src.api.context", fromlist=["get_rate_limit"]).get_rate_limit())
        set_rate_limit(None)
        self.assertEqual(60, __import__("src.api.context", fromlist=["get_rate_limit"]).get_rate_limit())

    def test_limit_matches_configured_value(self):
        set_rate_limit(1)
        limiter._windows.clear()
        self.assertIsNone(limiter.check("key-c"))
        self.assertIsNotNone(limiter.check("key-c"), "the first request past the configured limit must be limited")


if __name__ == "__main__":
    unittest.main()
