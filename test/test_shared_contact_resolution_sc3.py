"""Enforcement test for SC-SC3 (issue 1392): maintainer contact single source of truth.

Each of the 3 former call sites must derive maintainer contact text through one
shared resolution path — a get_maintainer_label() helper in src/frontend/ui_utils.py —
with no duplicated inline contact text.

RED: fails at baseline because no get_maintainer_label helper exists and the
call sites use inline f-strings with the mastodon_url pattern.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UI_UTILS = PROJECT_ROOT / "src" / "frontend" / "ui_utils.py"

CALL_SITES = [
    PROJECT_ROOT / "src" / "frontend" / "pages" / "login.py",
    PROJECT_ROOT / "streamlit_app.py",
]


def test_get_maintainer_label_helper_exists():
    """SC-3: ui_utils.py defines get_maintainer_label() taking no arguments,
    returning str, reading contact.maintainer_label from st.secrets."""
    assert UI_UTILS.exists(), f"missing file: {UI_UTILS}"
    tree = ast.parse(UI_UTILS.read_text(encoding="utf-8"), filename=str(UI_UTILS))
    helpers = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "get_maintainer_label"
    ]
    assert helpers, "no get_maintainer_label defined in src/frontend/ui_utils.py"
    helper = helpers[0]

    params = [arg.arg for arg in helper.args.args + helper.args.kwonlyargs]
    if helper.args.vararg:
        params.append(helper.args.vararg.arg)
    if helper.args.kwarg:
        params.append(helper.args.kwarg.arg)
    assert params == [], "get_maintainer_label must take no arguments"

    defaults = [
        d for d in helper.args.defaults + helper.args.kw_defaults if d is not None
    ]
    assert defaults == [], "get_maintainer_label must have no default arguments"

    src = ast.get_source_segment(UI_UTILS.read_text(encoding="utf-8"), helper)
    assert "st.secrets" in src, (
        "get_maintainer_label must read from st.secrets"
    )
    assert '"contact"' in src or "'contact'" in src, (
        "get_maintainer_label must read the 'contact' section from st.secrets"
    )
    assert "maintainer_label" in src, (
        "get_maintainer_label must read contact.maintainer_label"
    )


def test_all_three_call_sites_reference_helper():
    """SC-3: login.py show_unauthorized_dialog (1 site) and streamlit_app.py
    _initialize_database (2 sites) reference get_maintainer_label instead of
    inline mastodon_url contact f-strings."""
    # login.py: exactly one call site, referencing the helper
    login_tree = ast.parse(
        CALL_SITES[0].read_text(encoding="utf-8"), filename=str(CALL_SITES[0])
    )
    login_calls = [
        node
        for node in ast.walk(login_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "get_maintainer_label"
    ]
    assert login_calls, (
        "login.py does not call get_maintainer_label"
    )

    # streamlit_app.py: exactly two call sites inside _initialize_database
    app_tree = ast.parse(
        CALL_SITES[1].read_text(encoding="utf-8"), filename=str(CALL_SITES[1])
    )
    init_fn = [
        node
        for node in app_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_initialize_database"
    ]
    assert init_fn, "_initialize_database not found in streamlit_app.py"
    app_calls = [
        node
        for node in ast.walk(init_fn[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "get_maintainer_label"
    ]
    assert len(app_calls) == 2, (
        "streamlit_app.py _initialize_database must have exactly 2 "
        f"get_maintainer_label call sites, found {len(app_calls)}"
    )

    # No duplicated inline mastodon_url contact text in either call-site file
    for path in CALL_SITES:
        src = path.read_text(encoding="utf-8")
        assert "<MAINTAINER_CONTACT>" not in src, (
            f"{path.name} still contains inline MAINTAINER_CONTACT text"
        )
        assert "mastodon_url" not in src, (
            f"{path.name} still references mastodon_url for contact text"
        )
