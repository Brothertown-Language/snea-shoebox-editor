"""Enforcement test for SC-SC4 (issue 1392) under issue 1397 spec Revision 1 (SC-6):
default-fallback contact resolution — never crash on a missing contact key.

When ``contact.maintainer_label`` is absent from st.secrets, the app SHALL NOT
raise RuntimeError. Instead, startup continues: a ONE-TIME non-blocking
operator warning naming the missing key PATH only is emitted from the startup
preflight (not a dialog render), and ``st.set_page_config`` must remain the
first Streamlit command executed in ``main()``.

The startup path is invoked directly: ``main()`` is called with
``contact.maintainer_label`` absent and the sentinel CookieController proves
startup continued past the contact-key preflight into the next initialization
stage — a sentinel RuntimeError there means startup was NOT blocked by the
missing contact key.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import importlib
import logging
import re
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APP_MODULE = "streamlit_app"
SENTINEL_COOKIE_MSG = "SENTINEL: CookieController reached (no startup validation fired)"
MISSING_KEY_PATH = "contact.maintainer_label"

ST_COMMANDS_TO_RECORD = (
    "set_page_config",
    "spinner",
    "error",
    "exception",
    "info",
    "warning",
    "button",
    "stop",
    "rerun",
    "empty",
)


@pytest.fixture()
def recorded_st_calls(monkeypatch):
    """Record the invocation order of key Streamlit commands in main()."""
    st = importlib.import_module("streamlit")
    calls: list[str] = []
    originals: dict = {}

    def make_recorder(name, original):
        def wrapper(*args, **kwargs):
            calls.append(name)
            return original(*args, **kwargs)

        return wrapper

    for name in ST_COMMANDS_TO_RECORD:
        if hasattr(st, name):
            originals[name] = getattr(st, name)
            setattr(st, name, make_recorder(name, originals[name]))

    yield st, calls

    for name, original in originals.items():
        setattr(st, name, original)


@pytest.fixture()
def secrets_without_contact(monkeypatch, recorded_st_calls):
    """Make st.secrets lack the contact section entirely."""
    st, _ = recorded_st_calls
    fake_secrets = {"other_section": {"key": "value"}}
    monkeypatch.setattr(st, "secrets", fake_secrets, raising=False)
    return fake_secrets


@pytest.fixture()
def app_module(monkeypatch, recorded_st_calls):
    """Import streamlit_app with _initialize_database stubbed to a no-op.

    Sentinel: main() must proceed PAST the contact-key preflight and database
    init into CookieController construction. A sentinel there proves startup
    continued (no contact-key crash) while keeping main() from running
    further, making the continuation point deterministic.
    """
    st, _ = recorded_st_calls
    mod = importlib.import_module(APP_MODULE)
    monkeypatch.setattr(mod, "_initialize_database", lambda: None, raising=False)

    sentinel_module = types.ModuleType("streamlit_cookies_controller")

    class SentinelCookieController:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(SENTINEL_COOKIE_MSG)

    sentinel_module.CookieController = SentinelCookieController
    monkeypatch.setitem(sys.modules, "streamlit_cookies_controller", sentinel_module)
    return mod


def _capture_startup_warnings(caplog):
    """Capture warnings from the app logger (propagate=False in logging_config)."""
    logger = logging.getLogger("snea.app")
    logger.addHandler(caplog.handler)
    caplog.set_level(logging.WARNING, logger="snea.app")
    return logger


def _warning_messages_naming_missing_key(caplog) -> list[str]:
    return [
        rec.getMessage()
        for rec in caplog.records
        if rec.levelno >= logging.WARNING and MISSING_KEY_PATH in rec.getMessage()
    ]


def test_main_continues_with_single_operator_warning_naming_contact_maintainer_label(
    app_module, recorded_st_calls, secrets_without_contact, caplog
):
    """SC-4/SC-6 (Revision 1): startup must NOT crash on a missing
    contact.maintainer_label; instead exactly ONE operator warning naming the
    missing key PATH is emitted and startup continues into the next stage
    (proven by the sentinel CookieController RuntimeError)."""
    logger = _capture_startup_warnings(caplog)
    try:
        with pytest.raises(RuntimeError, match=re.escape(SENTINEL_COOKIE_MSG)):
            app_module.main()
    finally:
        logger.removeHandler(caplog.handler)

    warnings = _warning_messages_naming_missing_key(caplog)
    assert len(warnings) == 1, (
        "SC-6: exactly ONE operator warning naming contact.maintainer_label "
        f"must be emitted on missing contact.maintainer_label; got "
        f"{len(warnings)}: {warnings}"
    )


def test_set_page_config_is_first_streamlit_command(app_module, recorded_st_calls, secrets_without_contact):
    """SC-4: st.set_page_config must remain the first Streamlit command executed."""
    st, calls = recorded_st_calls
    try:
        app_module.main()
    except Exception:
        pass
    assert calls, "no Streamlit commands were recorded during startup"
    assert calls[0] == "set_page_config", (
        f"st.set_page_config must be the first Streamlit command in main(); recorded order: {calls}"
    )


def test_operator_warning_from_startup_preflight_not_dialog_render(
    app_module, recorded_st_calls, secrets_without_contact, caplog
):
    """SC-4/SC-6 (Revision 1): the operator warning is emitted from the
    startup preflight, not a dialog render.

    A dialog-render path would invoke other Streamlit commands (error/info/
    button) before the warning. Startup preflight must run directly after
    set_page_config with no intervening Streamlit rendering commands.
    """
    logger = _capture_startup_warnings(caplog)
    try:
        _, calls = recorded_st_calls
        try:
            app_module.main()
        except RuntimeError as exc:
            assert SENTINEL_COOKIE_MSG in str(exc), (
                f"startup was blocked before reaching the CookieController stage: {exc!r}"
            )
    finally:
        logger.removeHandler(caplog.handler)

    warnings = _warning_messages_naming_missing_key(caplog)
    assert warnings, "no operator warning naming contact.maintainer_label was emitted from startup preflight"
    render_commands = [c for c in calls if c != "set_page_config"]
    assert not render_commands, (
        f"warning was emitted after dialog/render commands {render_commands}; "
        "the operator warning must come from the startup preflight, not a "
        "dialog render"
    )
