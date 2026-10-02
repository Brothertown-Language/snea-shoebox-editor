"""Enforcement test for SC-SC3 (issue 1392): maintainer contact single source of truth.

Each of the 3 former call sites must derive maintainer contact text through one
shared resolution path — a get_maintainer_label() helper in src/frontend/ui_utils.py —
with no duplicated inline contact text.

Under issue 1397 SC-6 (spec Revision 1), the default-fallback resolution in
streamlit_app.resolve_maintainer_contact is the sanctioned shared fallback and
may reference ``contact.mastodon_url`` there; the no-duplication guarantee is
preserved by scoping mastodon_url references to that fallback only.

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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_maintainer_label"
    ]
    assert helpers, "no get_maintainer_label defined in src/frontend/ui_utils.py"
    helper = helpers[0]

    params = [arg.arg for arg in helper.args.args + helper.args.kwonlyargs]
    if helper.args.vararg:
        params.append(helper.args.vararg.arg)
    if helper.args.kwarg:
        params.append(helper.args.kwarg.arg)
    assert params == [], "get_maintainer_label must take no arguments"

    defaults = [d for d in helper.args.defaults + helper.args.kw_defaults if d is not None]
    assert defaults == [], "get_maintainer_label must have no default arguments"

    src = ast.get_source_segment(UI_UTILS.read_text(encoding="utf-8"), helper)
    assert "st.secrets" in src, "get_maintainer_label must read from st.secrets"
    assert '"contact"' in src or "'contact'" in src, (
        "get_maintainer_label must read the 'contact' section from st.secrets"
    )
    assert "maintainer_label" in src, "get_maintainer_label must read contact.maintainer_label"


def test_all_three_call_sites_reference_helper():
    """SC-3: login.py show_unauthorized_dialog (1 site) and streamlit_app.py
    _initialize_database (2 sites) reference get_maintainer_label instead of
    inline mastodon_url contact f-strings.

    Under issue 1397 SC-6 (spec Revision 1), the SC-6 fallback legitimately
    references ``contact.mastodon_url`` inside streamlit_app.py's
    ``resolve_maintainer_contact`` — that is the sanctioned shared fallback,
    not duplicated inline contact text. The no-duplication guarantee is
    preserved by asserting every mastodon_url reference in the call-site
    files lives inside the sanctioned shared helpers/fallback.
    """
    # login.py: exactly one call site, referencing the helper
    login_tree = ast.parse(CALL_SITES[0].read_text(encoding="utf-8"), filename=str(CALL_SITES[0]))
    login_calls = [
        node
        for node in ast.walk(login_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "get_maintainer_label"
    ]
    assert login_calls, "login.py does not call get_maintainer_label"

    # streamlit_app.py: exactly two call sites inside _initialize_database
    app_tree = ast.parse(CALL_SITES[1].read_text(encoding="utf-8"), filename=str(CALL_SITES[1]))
    init_fn = [
        node for node in app_tree.body if isinstance(node, ast.FunctionDef) and node.name == "_initialize_database"
    ]
    assert init_fn, "_initialize_database not found in streamlit_app.py"
    app_calls = [
        node
        for node in ast.walk(init_fn[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "get_maintainer_label"
    ]
    assert len(app_calls) == 2, (
        "streamlit_app.py _initialize_database must have exactly 2 "
        f"get_maintainer_label call sites, found {len(app_calls)}"
    )

    # No duplicated inline mastodon_url contact text in either call-site file.
    # SC-6 (Revision 1): the fallback's mastodon_url reference inside
    # streamlit_app.resolve_maintainer_contact is the sanctioned shared
    # fallback — allowed there, banned everywhere else.
    for path in CALL_SITES:
        src = path.read_text(encoding="utf-8")
        assert "<MAINTAINER_CONTACT>" not in src, f"{path.name} still contains inline MAINTAINER_CONTACT text"

    tree = ast.parse(CALL_SITES[1].read_text(encoding="utf-8"), filename=str(CALL_SITES[1]))
    sanctioned_scopes = {"resolve_maintainer_contact", "_CONTACT_FALLBACK_PATH"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "mastodon_url" in node.value:
                scope = _containing_definition(tree, node)
                assert scope in sanctioned_scopes, (
                    f"streamlit_app.py references mastodon_url outside the "
                    f"sanctioned SC-6 fallback (scope: {scope!r}): {node.value!r}"
                )

    login_src = CALL_SITES[0].read_text(encoding="utf-8")
    assert "mastodon_url" not in login_src, (
        f"{CALL_SITES[0].name} still references mastodon_url for contact "
        "text; it must go through the shared get_maintainer_contact_url helper"
    )


def _containing_definition(tree: ast.AST, node: ast.AST) -> str | None:
    """Return the name of the function/assignment node containing `node`."""
    for top in tree.body:
        if _contains(top, node):
            if isinstance(top, ast.FunctionDef):
                return top.name
            if isinstance(top, ast.Assign) and any(isinstance(t, ast.Name) for t in top.targets):
                return next(t.id for t in top.targets if isinstance(t, ast.Name))
    return None


def _contains(parent: ast.AST, node: ast.AST) -> bool:
    for child in ast.walk(parent):
        if child is node:
            return True
    return False
