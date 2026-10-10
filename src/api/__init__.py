# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Agent-facing read-only HTTP API bolted into the Streamlit/Tornado server (#1420).

All API code lives under this single parent package: the route registrar
(:mod:`src.api.registrar`), request authentication (:mod:`src.api.auth`), the
JSON error contract (:mod:`src.api.errors`), and per-endpoint route modules
(:mod:`src.api.routes`) that each declare their own path pattern.
"""
