# Copyright (c) 2026 Brothertown Language
import os
from playwright.sync_api import sync_playwright

def run():
    url = "http://backend:8787"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture console logs
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err.message}"))

        print(f"Navigating to {url}...")
        try:
            page.goto(url, timeout=30000)
            print("Page loaded. Waiting for Stlite to initialize...")
            
            # Wait for some content to appear
            # Stlite might take a while to load Pyodide and requirements
            # Wait for #stlite to be visible (means JS has loaded and replaced it)
            # OR for the loader to disappear
            print("Waiting for #stlite to be visible...")
            try:
                page.wait_for_selector("div#stlite", state="visible", timeout=60000)
                print("#stlite is visible.")
            except Exception as e:
                print(f"Timed out waiting for #stlite to be visible: {e}")
                
            # Look for common streamlit elements or our app's title
            # In app.py we have st.title("SNEA Online Shoebox Editor")
            try:
                # Increased timeout because Stlite/Wasm is slow
                # Streamlit titles are usually h1
                page.wait_for_selector("h1", timeout=60000)
                print(f"H1 element found: {page.inner_text('h1')}")
            except Exception:
                print("Timed out waiting for H1 element.")
            
            # Take a screenshot
            try:
                page.screenshot(path="landing_page.png", full_page=True)
                print("Screenshot saved to landing_page.png")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")
            
            # Log page content (limited)
            content = page.content()
            print(f"Page title: {page.title()}")
            print(f"Body text snippet: {content[:1000]}")
            
        except Exception as e:
            print(f"Error: {e}")
            # Even on error try to see what's there
            try:
                page.screenshot(path="/app/error_page.png")
                print("Error screenshot saved to /app/error_page.png")
                print(f"HTML snippet: {page.content()[:1000]}")
            except:
                pass
        finally:
            browser.close()

if __name__ == "__main__":
    run()
