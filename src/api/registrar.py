# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Bolt agent-facing API routes into the running Streamlit/Tornado app (#1420).

Streamlit has no public API for adding arbitrary HTTP routes. The mechanism —
empirically verified 2026-10-07 and re-verified by the Phase 0 probe on the
pinned stack (Streamlit 1.54.0 / Tornado 6.5.4) — is:

1. ``gc.get_objects()`` filtered to ``tornado.web.Application`` instances that
   expose ``wildcard_router.rules``
2. PREPEND ``tornado.web.Rule(tornado.routing.PathMatches(pattern), Handler)``
   entries to ``wildcard_router.rules`` — the specific endpoint rules first,
   then the ``/api/.*`` JSON-404 catch-all — so they sit ahead of Streamlit's
   own catch-all, which remains untouched behind the prepended block.

Guarantees:

- **Idempotent (R-3):** a module-level latch plus a structural route-presence
  check (scanning existing rules for the API's own path patterns) make repeat
  invocations — script reruns, distinct browser sessions, module reloads —
  no-ops. The probe's per-session ``st.session_state`` guard is NOT sufficient
  (session state is per-browser-session); hence the latch + structural check.
- **Self-check (R-4):** after bolting, a route-presence assertion is logged
  with rules found/inserted, order, pattern list, Application instance count,
  and the Streamlit + Tornado version numbers.
- **Failure mode (R-4):** if the Application or ``wildcard_router.rules``
  structure is missing (Streamlit internals changed on upgrade), the registrar
  logs a loud error naming the mismatch, leaves the API disabled, and raises
  nothing — the app keeps running normally. Never crash the UI.

This module runs inside the Streamlit script thread (invoked from
``streamlit_app.py`` after database initialization). Route *handlers* run
outside the script-runner context and must never use ``st.*`` APIs; they use
the database session factory captured here at bolt time.
"""

from __future__ import annotations

import gc
import threading

import streamlit
import tornado.routing
import tornado.web

from src.logging_config import get_logger

from .routes import api_not_found, records

logger = get_logger("src.api.registrar")

# Module object is created once per interpreter import: the latch persists
# across script reruns and distinct browser sessions, resetting only on
# interpreter restart or module reload (the structural check independently
# guards the reload case, where latch state would be recreated).
_bolted = False
_bolt_lock = threading.Lock()

# Route modules declare their own paths; specific endpoints first, then the
# JSON-404 catch-all. Order matters: first match wins.
_ROUTE_MODULES = (records, api_not_found)


def _api_patterns() -> list[str]:
    return [module.PATH for module in _ROUTE_MODULES]


def _find_applications() -> list[tornado.web.Application]:
    """Live Application instances exposing the internal routing structure."""
    found = []
    for obj in gc.get_objects():
        if not isinstance(obj, tornado.web.Application):
            continue
        wildcard_router = getattr(obj, "wildcard_router", None)
        if wildcard_router is not None and hasattr(wildcard_router, "rules"):
            found.append(obj)
    return found


def _rule_pattern(rule) -> str | None:
    """Extract the path pattern from a routing rule.

    Tornado 6.5.4's ``PathMatches`` keeps no ``path_pattern`` attribute — the
    pattern survives only as the compiled ``regex`` (pattern source with a
    trailing ``$`` appended). Strip that suffix to recover the original
    pattern string for structural comparison.
    """
    matcher = getattr(rule, "matcher", None)
    if matcher is None:
        return None
    regex = getattr(matcher, "regex", None)
    if regex is not None:
        pattern = regex.pattern
        if pattern.endswith("$"):
            pattern = pattern[:-1]
        return pattern
    return getattr(matcher, "path_pattern", None)


def _present_patterns(app: tornado.web.Application) -> set[str]:
    """Path patterns of already-bolted API rules on this application."""
    api_patterns = set(_api_patterns())
    return {
        pattern for pattern in (_rule_pattern(rule) for rule in app.wildcard_router.rules) if pattern in api_patterns
    }


def install_api_routes(db_session_factory, rate_limit_per_minute: int | None = None) -> None:
    """Bolt the API routes into the running Tornado application(s).

    Called from ``streamlit_app.py`` at first script run, after database
    initialization. ``db_session_factory`` is a bound ``sessionmaker`` (or
    equivalent zero-argument callable returning a session) captured for
    handler use — handlers never touch ``st.*`` (R-2).
    ``rate_limit_per_minute`` (R-14) is read from secrets by the caller in
    the script thread and captured here for the request-time limiter.
    Never raises (R-4).
    """
    global _bolted
    if _bolted:
        return

    with _bolt_lock:
        if _bolted:  # re-check under the lock
            return

        try:
            from .context import set_rate_limit, set_session_factory

            set_session_factory(db_session_factory)
            set_rate_limit(rate_limit_per_minute)

            apps = _find_applications()
            if not apps:
                logger.error(
                    "API bolt FAILED: no live tornado.web.Application with "
                    "wildcard_router.rules was found — agent-facing API is "
                    "DISABLED (streamlit %s / tornado %s). The UI is unaffected.",
                    getattr(streamlit, "__version__", "unknown"),
                    _tornado_version(),
                )
                return

            inserted_per_app = []
            for app in apps:
                present = _present_patterns(app)
                if len(present) == len(_ROUTE_MODULES):
                    # Structural check: another code path (module reload) already
                    # bolted this application — do not stack duplicate rules.
                    continue
                # Prepend catch-all first, then specific endpoints, so the final
                # rule order is [endpoints..., catch-all, ...Streamlit's rules].
                rules_to_insert = [
                    (
                        module.PATH,
                        module.HANDLER,
                    )
                    for module in reversed(_ROUTE_MODULES)
                ]
                for pattern, handler in rules_to_insert:
                    if pattern in present:
                        continue
                    rule = tornado.web.Rule(tornado.routing.PathMatches(pattern), handler)
                    app.wildcard_router.rules.insert(0, rule)
                inserted_per_app.append(app)

            patterns = _api_patterns()
            logger.info(
                "API bolt self-check: routes %s bolted at the FRONT of "
                "wildcard_router.rules (specific endpoint first, then the "
                "/api/.* JSON-404 catch-all; Streamlit's own routes remain "
                "behind the prepended block) | applications found=%d, "
                "bolted=%d | streamlit %s | tornado %s",
                patterns,
                len(apps),
                len(inserted_per_app),
                getattr(streamlit, "__version__", "unknown"),
                _tornado_version(),
            )
            _bolted = True
        except Exception:
            # R-4: no exception may propagate into the UI script path.
            logger.exception(
                "API bolt FAILED with an unexpected error — agent-facing API "
                "is DISABLED; the app continues running normally."
            )


def _tornado_version() -> str:
    import tornado

    return tornado.version
