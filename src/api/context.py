# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Request-time context for API route handlers (#1420).

Holds the database session factory captured at bolt time (inside the
Streamlit script thread, where the shared engine is established). Handlers
run outside the script-runner context and read the factory from here — they
never touch ``st.*`` APIs (R-2).
"""

from __future__ import annotations

import threading

_lock = threading.Lock()
_session_factory = None
_rate_limit_per_minute = 60  # default (R-14); captured at bolt time

DEFAULT_RATE_LIMIT_PER_MINUTE = 60


def set_session_factory(factory) -> None:
    """Capture the session factory at bolt time (script thread)."""
    global _session_factory
    with _lock:
        _session_factory = factory


def get_session_factory():
    """Return the captured session factory, or None before the bolt."""
    with _lock:
        return _session_factory


def set_rate_limit(limit: int | None) -> None:
    """Capture the per-key rate limit at bolt time (script thread).

    ``None`` or a non-positive value selects the default (60/min).
    Handlers never read ``st.secrets`` themselves (R-2).
    """
    global _rate_limit_per_minute
    with _lock:
        _rate_limit_per_minute = limit if limit and limit > 0 else DEFAULT_RATE_LIMIT_PER_MINUTE


def get_rate_limit() -> int:
    """Per-key request limit per 60-second window."""
    with _lock:
        return _rate_limit_per_minute
