"""Shared Playwright harness for Issue #1413 pagination-relocation E2E tests.

Worker-thread browser-session pattern from test_semantic_search_ui_flow_e2e.py
(pytest 9 + anyio keeps an asyncio loop on the main thread; the Playwright sync
API forbids entering under a running loop). With SNEA_E2E=1 the app-side
TEST-ONLY auth bypass (Issue #1400 SC-11) authenticates a fresh context.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import queue
import threading

from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/records"
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")


def require_auth_storage() -> str | None:
    """SNEA_E2E=1 → fresh context via the test-only bypass; no saved state."""
    if os.environ.get("SNEA_E2E") == "1":
        return None
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "regenerate via the headed-login procedure in test/ui/AGENTS.md."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


class BrowserSession:
    """A Chromium + authed context + page living entirely inside one worker
    thread. Test bodies are queued into that thread via run()."""

    def __init__(self, storage: str | None):
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
            context = browser.new_context(viewport={"width": 1280, "height": 900}, storage_state=self._storage)
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

    def run(self, fn, timeout: float = 240.0):
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


def goto_records(page: Page):
    """Navigate to the Records page and wait for the app to settle."""
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if page.url.rstrip("/").endswith("/login"):
        raise AssertionError("App redirected to /login — auth state is stale; regenerate per test/ui/AGENTS.md.")
    page.wait_for_selector('[data-testid="stRadio"] input[type="radio"]', state="attached", timeout=45_000)
    page.wait_for_timeout(1500)


def body_text(page: Page) -> str:
    return page.evaluate("() => document.body.innerText")


def sidebar_text(page: Page) -> str:
    return page.evaluate(
        "() => { const sb = document.querySelector('[data-testid=\"stSidebar\"]');"
        " return sb ? sb.innerText : ''; }"
    )


def main_buttons(page: Page, label: str):
    """Buttons whose text contains the label OUTSIDE the sidebar (main panel).
    contains() tolerates icon glyphs rendered alongside the label text."""
    return page.locator(
        f'//button[contains(normalize-space(), "{label}")'
        f' and not(ancestor::div[@data-testid="stSidebar"])]'
    )


def sidebar_buttons(page: Page, label: str):
    """Buttons whose text contains the label INSIDE the sidebar."""
    return page.locator(
        f'//button[contains(normalize-space(), "{label}")'
        f' and ancestor::div[@data-testid="stSidebar"]]'
    )
