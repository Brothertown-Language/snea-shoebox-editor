# Copyright (c) 2026 Brothertown Language
import os
import pytest
import time
from playwright.sync_api import Page, expect, sync_playwright
import socket

# Enable Playwright tracing and artifacts to avoid post-failure hangs
def pytest_addoption(parser):
    parser.addoption("--tracing", action="store", default="retain-on-failure")
    parser.addoption("--screenshot", action="store", default="only-on-failure")
    parser.addoption("--video", action="store", default="retain-on-failure")


# Global per-test timeout via marker; can be overridden by CLI --timeout
@pytest.mark.timeout(60)
def test_app_loads():
    # Log console messages
    def handle_console(msg):
        print(f"BROWSER CONSOLE: [{msg.type}] {msg.text}")

    # We will create the browser/page only after prechecks

    # We use the service name 'web' as defined in docker/docker-compose.yml
    # Allow overriding retries via env to help diagnose hangs in CI
    max_retries = int(os.environ.get("SNEA_UI_MAX_RETRIES", "3"))
    host = "web"
    port = 8501
    url = f"http://{host}:{port}"

    # Ensure the Docker DNS name resolves and port is reachable before navigation
    print("START: test_app_loads -> DNS/port precheck")
    try:
        resolved = socket.gethostbyname(host)
        print(f"Resolved {host} -> {resolved}")
        with socket.create_connection((host, port), timeout=2) as s:
            print(f"TCP connect to {host}:{port} OK")
    except Exception as e:
        pytest.fail(f"Precheck failed: cannot resolve/connect to {host}:{port}: {e}")
    
    # Launch browser only after prechecks, to avoid fixture hangs
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on("console", handle_console)
        page.on("pageerror", lambda exc: pytest.fail(f"Browser-side exception: {exc}"))

        # Start tracing and ensure it is stopped regardless of failures
        try:
            page.context.tracing.start(screenshots=True, snapshots=True)
        except Exception as e:
            print(e)
            pass

        for i in range(max_retries):
            try:
                print("START: test_app_loads -> navigating to app")
                response = page.goto(url, timeout=15000)
                if response and response.ok:
                    # Streamlit uses specific selectors
                    print("START: test_app_loads -> asserting login button visible")
                    expect(page.get_by_role("button", name="Log in with GitHub")).to_be_visible(timeout=15000)
                    
                    break
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
                if i == max_retries - 1:
                    # Capture page content on final failure
                    print(f"PAGE CONTENT ON FINAL ATTEMPT FAILURE: {page.content()}")
                    raise
                time.sleep(5)
    
    # Note: page, context, browser are closed in finally block below
    try:
        pass # placeholder
    finally:
        # Ensure we always close the page to avoid teardown hangs
        try:
            page.context.tracing.stop(path="test_app_loads_trace.zip")
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
