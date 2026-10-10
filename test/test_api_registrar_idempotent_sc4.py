# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Registrar idempotency tests — issue #1420, SC-4.

The bolt is a no-op when the routes are already present: repeated registrar
invocations (script reruns, distinct browser sessions, module reloads) leave
exactly one rule per API pattern — no duplicates.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import unittest

import tornado.web

from src.api import registrar


def _api_rule_count(app: tornado.web.Application) -> int:
    """Count rules whose matcher path pattern is one of the API patterns."""
    patterns = set(registrar._api_patterns())
    return sum(1 for rule in app.wildcard_router.rules if registrar._rule_pattern(rule) in patterns)


class RegistrarIdempotencyTests(unittest.TestCase):
    def setUp(self):
        registrar._bolted = False
        self.app = tornado.web.Application()

    def tearDown(self):
        registrar._bolted = False

    def test_first_bolt_inserts_exactly_one_rule_per_pattern(self):
        registrar.install_api_routes(lambda: None)
        self.assertEqual(_api_rule_count(self.app), len(registrar._api_patterns()))

    def test_repeated_invocation_with_active_latch_is_noop(self):
        registrar.install_api_routes(lambda: None)
        before = len(self.app.wildcard_router.rules)
        for _ in range(5):
            registrar.install_api_routes(lambda: None)
        self.assertEqual(len(self.app.wildcard_router.rules), before)

    def test_module_reload_latch_reset_still_noop_via_structural_check(self):
        registrar.install_api_routes(lambda: None)
        before = len(self.app.wildcard_router.rules)
        # Simulate a module reload: latch state recreated, fresh import.
        registrar._bolted = False
        registrar.install_api_routes(lambda: None)
        self.assertEqual(len(self.app.wildcard_router.rules), before)
        self.assertEqual(_api_rule_count(self.app), len(registrar._api_patterns()))

    def test_rule_order_specific_endpoint_before_catchall(self):
        registrar.install_api_routes(lambda: None)
        patterns = [registrar._rule_pattern(rule) for rule in self.app.wildcard_router.rules]
        api_positions = [i for i, p in enumerate(patterns) if p in set(registrar._api_patterns())]
        ordered = [patterns[i] for i in sorted(api_positions)]
        self.assertEqual(
            ordered.index("/api/v1/records"),
            0,
            f"specific endpoint must be first, got {ordered}",
        )
        self.assertLess(
            ordered.index("/api/v1/records"),
            ordered.index("/api/.*"),
            f"catch-all must follow the specific endpoint, got {ordered}",
        )

    def test_prepend_lands_ahead_of_streamlit_rules(self):
        # Seed a Streamlit-like catch-all behind the bolt position.
        self.app.add_handlers(".*$", [(r"/.*", tornado.web.RequestHandler)])
        registrar.install_api_routes(lambda: None)
        patterns = [registrar._rule_pattern(rule) for rule in self.app.wildcard_router.rules]
        self.assertEqual(patterns[0], "/api/v1/records")
        self.assertEqual(patterns[1], "/api/.*")


if __name__ == "__main__":
    unittest.main()
