"""Issue #1385 SC-1/SC-2/SC-8 — Playwright real-browser DOM assertions for the
Records page semantic-search UI (mode radio, threshold control persistence,
language-filter gating). No search execution, no embedding-model invocation.

Harness: ONE module-scoped Chromium session (launched in a worker thread —
pytest 9 + anyio keeps an asyncio loop on the main thread and the Playwright
sync API forbids entering under a running loop). All three checks share that
session with a context loaded from tmp/issue-36/auth-state.json (verified
admin OAuth state). One page.goto per test (3 total); interactions poll with
wait_for selectors/functions (~10-15s) instead of fixed sleeps.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import json
import os
import queue
import threading

import pytest
from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1385", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

MODES = ["Headword", "Gloss", "Lexeme", "FTS", "Semantic Gloss", "Semantic All"]
THRESHOLD_TOOLTIP = "Applies only in Semantic modes."
LANG_FILTER_HELP = "Language filters are not applied in Semantic search modes."
LANG_ROLE_HELP = "Language Role filters are not applied in Semantic search modes."

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _require_auth_storage() -> str:
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


class _BrowserSession:
    """A Chromium + authed context + page living entirely inside one worker
    thread. Test bodies are queued into that thread via run(); results and
    exceptions propagate back to the pytest thread."""

    def __init__(self, storage: str):
        self._jobs: queue.Queue = queue.Queue()
        self._result_box: list[BaseException | None] = []
        self._done_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._shutdown = threading.Event()
        self._storage = storage
        self.thread = threading.Thread(target=self._main, daemon=True)
        self.thread.start()
        self._ready_evt.wait(timeout=60)

    def _main(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(storage_state=self._storage)
            page = context.new_page()
            self._ready_evt.set()
            while not self._shutdown.is_set():
                try:
                    fn = self._jobs.get(timeout=0.2)
                except queue.Empty:
                    continue
                if fn is None:
                    break
                self._result_box.clear()
                try:
                    fn(page)
                    self._result_box.append(None)
                except BaseException as e:  # noqa: BLE001 — propagate verbatim
                    self._result_box.append(e)
                self._done_evt.set()
            browser.close()

    def run(self, fn, timeout: float = 180.0):
        self._done_evt.clear()
        self._jobs.put(fn)
        if not self._done_evt.wait(timeout=timeout):
            raise TimeoutError(f"test body exceeded {timeout}s in worker thread")
        err = self._result_box[0] if self._result_box else RuntimeError("worker returned no result")
        if err is not None:
            raise err

    def close(self):
        self._shutdown.set()
        self._jobs.put(None)
        self.thread.join(timeout=30)


@pytest.fixture(scope="module")
def session():
    storage = _require_auth_storage()
    sess = _BrowserSession(storage)
    yield sess
    sess.close()


# ---------- shared page helpers (run inside the worker thread) ----------


MODE_INDEX = {m: i for i, m in enumerate(MODES)}


def _goto_records(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    # Sidebar search UI rendered — wait for the mode radio inputs.
    page.wait_for_selector('[data-testid="stRadio"] input[type="radio"]', state="attached", timeout=45_000)
    page.wait_for_function(
        """() => {
        const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
        const g = groups.find(x => x.textContent.includes('Search Mode'));
        return g && g.querySelectorAll('input[type="radio"]').length >= 6;
    }""",
        timeout=15_000,
    )
    page.wait_for_timeout(1000)  # small settle for Streamlit first-rerun widgets


MODE_GROUP = """() => {
    const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
    return groups.find(g => g.textContent.includes('Search Mode'));
}"""


def _mode_label(page: Page, index: int):
    """Streamlit hides the radio inputs; click the visible radio LABEL."""
    return page.locator('[data-testid="stRadio"] label[data-baseweb="radio"]').nth(index)


def _select_mode(page: Page, mode: str):
    _mode_label(page, MODE_INDEX[mode]).click()


def _mode_checked(page: Page) -> int:
    return page.evaluate(
        """() => {
        const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
        const g = groups.find(x => x.textContent.includes('Search Mode'));
        return Array.from(g.querySelectorAll('input[type="radio"]')).findIndex(x => x.checked);
    }"""
    )


def _wait_for_body_text(page: Page, fragment: str, timeout: int = 15_000):
    page.wait_for_function(
        "frag => document.body.textContent.includes(frag)",
        arg=fragment,
        timeout=timeout,
    )


def _wait_for_body_text_absent(page: Page, fragment: str, timeout: int = 15_000):
    page.wait_for_function(
        "frag => !document.body.textContent.includes(frag)",
        arg=fragment,
        timeout=timeout,
    )


def _ui_state(page: Page) -> dict:
    """One-page-evaluate DOM state snapshot for the threshold + filter widgets."""
    return page.evaluate(
        """() => {
        const out = {};
        // Threshold slider: aria-valuenow + disabled state via the group label.
        const sg = document.querySelector('[data-testid="stSlider"]');
        const role = sg ? sg.querySelector('[role="slider"]') : null;
        out.slider_valuenow = role ? role.getAttribute('aria-valuenow') : null;
        out.slider_group_disabled = sg
            ? sg.querySelector('label[data-testid="stWidgetLabel"]').getAttribute('disabled') !== null
            : null;
        const num = document.querySelector('input[type="number"]');
        out.number_value = num ? num.value : null;
        out.number_disabled = num ? num.disabled : null;
        // Language selectbox (2nd stSelectbox in the sidebar).
        const sel = Array.from(document.querySelectorAll('[data-testid="stSelectbox"]'));
        const lang = sel.find(x => x.textContent.includes('Select Language'));
        out.language_present = !!lang;
        out.language_disabled = lang
            ? lang.querySelector('label[data-testid="stWidgetLabel"]').getAttribute('disabled') !== null
            : null;
        // Language Role radios: 2nd stRadio group.
        const grp = Array.from(document.querySelectorAll('[data-testid="stRadio"]'))
            .find(x => x.textContent.includes('Language Role'));
        out.langrole_disabled = grp
            ? Array.from(grp.querySelectorAll('input')).map(i => i.disabled)
            : null;
        return out;
    }"""
    )


def _slider_value(page: Page) -> float:
    page.wait_for_selector('[data-testid="stSlider"] [role="slider"]', timeout=15_000)
    return float(_ui_state(page)["slider_valuenow"])


# ---------- SC-1 ----------


CAPTIONS = {
    "Semantic Gloss": "Semantic search over English glosses",
    "Semantic All": "Semantic search over all fields",
}


def _sc1_flow(page: Page):
    _goto_records(page)
    # All 6 mode entries present: radio inputs in the Search Mode group.
    n = page.evaluate(
        """() => {
        const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
        const g = groups.find(x => x.textContent.includes('Search Mode'));
        return g.querySelectorAll('input[type="radio"]').length;
    }"""
    )
    assert n == 6, f"expected 6 mode radio options; got {n}"
    for idx, mode in enumerate(MODES):
        _mode_label(page, idx).wait_for(state="visible", timeout=10_000)

    # Select Semantic Gloss → its caption appears under the radio.
    _select_mode(page, "Semantic Gloss")
    page.wait_for_timeout(1000)
    _wait_for_body_text(page, CAPTIONS["Semantic Gloss"])
    assert _mode_checked(page) == MODE_INDEX["Semantic Gloss"]
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc1-radio.png"))

    # Select Semantic All → caption switches.
    _select_mode(page, "Semantic All")
    page.wait_for_timeout(1000)
    _wait_for_body_text(page, CAPTIONS["Semantic All"])
    assert _mode_checked(page) == MODE_INDEX["Semantic All"]


def test_sc1_mode_radio_options(session):
    session.run(_sc1_flow)


# ---------- SC-2 ----------


def _sc2_flow(page: Page):
    _goto_records(page)

    # Select Semantic Gloss → threshold widgets enabled and rendered.
    _select_mode(page, "Semantic Gloss")
    page.wait_for_timeout(1500)
    _wait_for_body_text(page, CAPTIONS["Semantic Gloss"])
    page.wait_for_function(
        """() => {
        const sg = document.querySelector('[data-testid="stSlider"]');
        const role = sg ? sg.querySelector('[role="slider"]') : null;
        const num = document.querySelector('input[type="number"]');
        return role && num && num.disabled === false;
    }""",
        timeout=15_000,
    )
    st = _ui_state(page)
    assert not st["slider_group_disabled"], (
        f"threshold slider unexpectedly disabled in Semantic Gloss mode: {st}"
    )

    # Set numeric input to 0.7 and commit; slider must follow (two-way coupling).
    page.locator('input[type="number"]').fill("0.7")
    page.keyboard.press("Enter")
    page.wait_for_function(
        """() => {
        const r = document.querySelector('[data-testid="stSlider"] [role="slider"]');
        return r && Math.abs(parseFloat(r.getAttribute('aria-valuenow')) - 0.7) < 0.011;
    }""",
        timeout=15_000,
    )
    after = _slider_value(page)
    assert abs(after - 0.7) < 0.011, f"slider value {after} did not follow numeric edit 0.7"
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc2-threshold-semantic.png"))

    # Reload → PreferenceService round-trip: control re-renders persisted 0.7.
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="stSlider"] [role="slider"]', timeout=45_000)
    page.wait_for_timeout(1500)
    persisted = _slider_value(page)
    assert abs(persisted - 0.7) < 0.011, (
        f"threshold persisted value {persisted} != 0.7 after reload"
    )

    # Switch to Headword → control still rendered (stable slot) and disabled,
    # with the "Applies only in Semantic modes." help text surfaced on hover.
    _select_mode(page, "Headword")
    page.wait_for_timeout(1500)
    page.wait_for_selector('[data-testid="stSlider"] [role="slider"]', timeout=15_000)
    page.wait_for_selector('input[type="number"]', timeout=15_000)
    st2 = _ui_state(page)
    assert st2["slider_group_disabled"], f"threshold slider not disabled in Headword mode: {st2}"
    assert st2["number_disabled"], f"threshold number input not disabled in Headword mode: {st2}"
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc2-threshold-disabled.png"))

    # Help text: Streamlit renders tooltip content lazily on hover; a raw
    # JS mouseover dispatch on the hover target mounts the content node.
    _hover_tooltip(page, "Help for Semantic threshold", THRESHOLD_TOOLTIP)


def test_sc2_threshold_control_and_persistence(session):
    session.run(_sc2_flow)


# ---------- SC-8 ----------


def _wait_for_rerun(page: Page, checked_index: int, timeout: int = 15_000):
    """Wait for the Streamlit rerun triggered by the mode change to settle."""
    page.wait_for_timeout(1500)
    page.wait_for_function(
        """idx => {
        const groups = Array.from(document.querySelectorAll('[data-testid="stRadio"]'));
        const g = groups.find(x => x.textContent.includes('Search Mode'));
        if (!g) return false;
        const inputs = g.querySelectorAll('input[type="radio"]');
        return inputs[idx] && inputs[idx].checked;
    }""",
        arg=checked_index,
        timeout=timeout,
    )


def _hover_tooltip(page: Page, aria_label: str, expected_text: str, timeout: int = 10_000):
    """Mount a Streamlit help tooltip's content: dispatch mouseover on the
    target whose button carries the given aria-label, then wait for a tooltip
    content node whose text matches expected_text exactly."""
    mounted = page.evaluate(
        """label => {
        const targets = Array.from(document.querySelectorAll('[data-testid="stTooltipHoverTarget"]'));
        const t = targets.find(x => {
            const b = x.querySelector('button');
            return b && b.getAttribute('aria-label') === label;
        });
        if (!t) return false;
        ['mouseover','mouseenter','pointerover'].forEach(ev =>
            t.dispatchEvent(new MouseEvent(ev, {bubbles: true})));
        return true;
    }""",
        aria_label,
    )
    assert mounted, f"tooltip hover target not found for {aria_label!r}"
    page.wait_for_function(
        """txt => {
        const contents = Array.from(
            document.querySelectorAll('[data-testid="stTooltipContent"], [role="tooltip"]')
        );
        return contents.some(c => c.textContent.trim() === txt);
    }""",
        arg=expected_text,
        timeout=timeout,
    )
    return expected_text


def _assert_filters(page: Page, semantic: bool):
    st = _ui_state(page)
    if semantic:
        assert st["language_present"], f"language selectbox missing in semantic mode: {st}"
        assert st["language_disabled"], f"language selectbox not disabled in semantic mode: {st}"
        assert st["langrole_disabled"] == [True, True, True], (
            f"language-role radios not all disabled in semantic mode: {st['langroleDisabled']}"
        )
    else:
        assert st["language_present"], f"language selectbox missing in Headword mode: {st}"
        assert not st["language_disabled"], (
            f"language selectbox unexpectedly disabled in Headword mode: {st}"
        )
        assert st["langrole_disabled"] == [False, False, False], (
            f"language-role radios unexpectedly disabled in Headword mode: {st['langroleDisabled']}"
        )


def _sc8_flow(page: Page):
    _goto_records(page)

    # Semantic Gloss: filters disabled + help text mentions filters not applied.
    _select_mode(page, "Semantic Gloss")
    _wait_for_rerun(page, MODE_INDEX["Semantic Gloss"])
    _wait_for_body_text(page, CAPTIONS["Semantic Gloss"])
    _hover_tooltip(page, "Help for Select Language", LANG_FILTER_HELP)
    _hover_tooltip(page, "Help for Language Role", LANG_ROLE_HELP)
    _assert_filters(page, semantic=True)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "e2e-sc8-filters.png"))

    # Semantic All: same gating.
    _select_mode(page, "Semantic All")
    _wait_for_rerun(page, MODE_INDEX["Semantic All"])
    _wait_for_body_text(page, CAPTIONS["Semantic All"])
    _assert_filters(page, semantic=True)

    # Headword: filters enabled, help texts gone.
    _select_mode(page, "Headword")
    _wait_for_rerun(page, MODE_INDEX["Headword"])
    _wait_for_body_text(page, "Algonquian headwords")
    _assert_filters(page, semantic=False)
    _wait_for_body_text_absent(page, "not applied in Semantic search modes.")


def test_sc8_language_filters_disabled(session):
    session.run(_sc8_flow)