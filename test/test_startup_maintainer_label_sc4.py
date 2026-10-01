"""Enforcement test for SC-SC4 (issue 1392): fail fast on missing contact.maintainer_label.

When ``contact.maintainer_label`` is absent from st.secrets, the app SHALL fail
fast during startup with an actionable error naming ``contact.maintainer_label``
— no silent default — and ``st.set_page_config`` must remain the first
Streamlit command executed in ``main()``.

The startup path is invoked directly: ``main()`` is called with
``contact.maintainer_label`` absent and an assertion verifies the actionable
error is raised from startup initialization (not from a dialog-render call).

RED: fails at baseline because no startup validation exists in main().

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APP_MODULE = "streamlit_app"
SENTINEL_COOKIE_MSG = "SENTINEL: CookieController reached (no startup validation fired)"

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
    """Import streamlit_app with _initialize_database stubbed to a no-op."""
    st, _ = recorded_st_calls
    mod = importlib.import_module(APP_MODULE)
    monkeypatch.setattr(mod, "_initialize_database", lambda: None, raising=False)

    # Sentinel: if startup validation does not fire, main() proceeds past
    # database init into CookieController construction. A sentinel there makes
    # baseline failure deterministic and clearly distinguishable.
    sentinel_module = types.ModuleType("streamlit_cookies_controller")

    class SentinelCookieController:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(SENTINEL_COOKIE_MSG)

    sentinel_module.CookieController = SentinelCookieController
    monkeypatch.setitem(sys.modules, "streamlit_cookies_controller", sentinel_module)
    return mod


def test_main_fails_fast_naming_contact_maintainer_label(
    app_module, recorded_st_calls, secrets_without_contact
):
    """SC-4: startup must raise an actionable error naming contact.maintainer_label."""
    _, calls = recorded_st_calls
    with pytest.raises(Exception, match=r"contact\.maintainer_label"):
        app_module.main()


def test_set_page_config_is_first_streamlit_command_before_fail_fast(
    app_module, recorded_st_calls, secrets_without_contact
):
    """SC-4: st.set_page_config must remain the first Streamlit command executed."""
    st, calls = recorded_st_calls
    try:
        app_module.main()
    except Exception:
        pass
    assert calls, "no Streamlit commands were recorded during startup"
    assert calls[0] == "set_page_config", (
        f"st.set_page_config must be the first Streamlit command in main(); "
        f"recorded order: {calls}"
    )


def test_fail_fast_raises_from_startup_not_dialog_render(
    app_module, recorded_st_calls, secrets_without_contact
):
    """SC-4: the error is raised from startup initialization, not a dialog render.

    A dialog-render path would invoke other Streamlit commands (error/info/
    button) before the failure. Startup fail-fast must raise directly after
    set_page_config with no intervening Streamlit rendering commands.
    """
    _, calls = recorded_st_calls
    try:
        app_module.main()
    except Exception as exc:
        message = str(exc)
        assert "contact.maintainer_label" in message, (
            f"raised error is not actionable: {message!r}"
        )
        render_commands = [c for c in calls if c != "set_page_config"]
        assert not render_commands, (
            f"error was raised after dialog/render commands {render_commands}; "
            "fail-fast must come from startup initialization, not a dialog render"
        )
        assert SENTINEL_COOKIE_MSG not in message, (
            "no startup validation fired; main() ran past startup initialization"
        )
    else:
        pytest.fail(
            "main() completed without failing fast on missing contact.maintainer_label"
        )