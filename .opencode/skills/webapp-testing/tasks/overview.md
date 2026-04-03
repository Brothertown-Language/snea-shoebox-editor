# Task: overview

Web application testing toolkit using Playwright for local app verification, debugging, UI behavior validation, screenshots, and browser logs.

## When to Invoke

Use this skill when you need to:
- Test local web applications
- Verify frontend functionality  
- Debug UI behavior
- Capture browser screenshots
- View browser console logs
- Validate page interactions

## Prerequisites

1. Playwright must be installed
2. Local web application must be running
3. Valid URL for the application

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Procedure

1. **Launch Browser**
   - Use `playwright` MCP tool to launch browser
   - Navigate to application URL
   - Wait for page load

2. **Interact with Page**
   - Click elements with `page.click()`
   - Fill forms with `page.fill()`
   - Wait for selectors with `page.waitForSelector()`

3. **Verify State**
   - Check element visibility
   - Validate text content
   - Verify URL changes
   - Assert page state

4. **Capture Artifacts**
   - Take screenshots with `page.screenshot()`
   - Extract console logs
   - Capture network requests

5. **Report Results**
   - Document test outcomes
   - Include screenshots in issue comments
   - Report any console errors

## Best Practices

- **Use bundled scripts as black boxes** - Check `scripts/` for helpers before writing custom code
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
- **Always run scripts with `--help` first** - avoid reading large source files

## Common Use Cases

### Test Page Load
```
1. Launch browser
2. Navigate to URL
3. Wait for page to load
4. Verify title/main element
5. Screenshot page
```

### Test Form Submission
```
1. Navigate to form page
2. Fill required fields
3. Click submit button
4. Wait for response
5. Verify success/error message
```

### Debug UI Issue
```
1. Launch browser
2. Reproduce problematic behavior
3. Capture console logs
4. Take screenshot of issue
5. Report findings
```

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

## Important Notes

- Always close browser pages after testing
- Screenshots should be attached to issue comments
- Console errors should be investigated before declaring tests complete
- Never test against production URLs - local only
- Use descriptive names for screenshots

## Cross-References

- Related: `engineering-approach` skill (testing verification)
- Related: AGENTS.md verification requirements
- Tools: Playwright browser automation