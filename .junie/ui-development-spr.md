<!-- Copyright (c) 2026 Brothertown Language -->
# SNEA Editor UI Development Guidelines

## CRITICAL: stlite ONLY (WebAssembly in Browser)

### Architecture Requirements
- **Production:** stlite (Streamlit compiled to WebAssembly via Pyodide)
- **Local Development:** MUST use stlite (same as production)
- **NO regular Streamlit server** - local dev must match production environment
- **Deployment:** Bundle via `uv run python scripts/bundle_stlite.py` → `dist/index.html`
- **Runtime:** Runs entirely in browser, no Python server required

### Testing UI Changes
```bash
# Build stlite bundle
uv run python scripts/bundle_stlite.py

# Open in browser
# Then open dist/index.html in your browser
```

## Framework Specifics (Streamlit API in stlite)

### State Management
- **Session State:** `st.session_state` - persists across reruns within browser session
- **Example:**
  ```python
  if "user" not in st.session_state:
      st.session_state.user = None
  ```

### Layout Components
- **Columns:** `st.columns([2, 1, 4, 1])` - proportional width layout
- **Containers:** `st.container()` - group elements
- **Tabs:** `st.tabs(["Tab1", "Tab2"])` - tabbed interface
- **Expander:** `st.expander("Details")` - collapsible sections
- **Sidebar:** `st.sidebar` - persistent side navigation

### Navigation
- **Query Parameters:** `st.query_params` - URL-based routing
  ```python
  st.query_params["view"] = "edit"
  current_view = st.query_params.get("view", "list")
  ```
- **Rerun:** `st.rerun()` - trigger full page refresh

### Input Widgets
- **Text Input:** `st.text_input("Label", value="default")`
- **Text Area:** `st.text_area("Label", value="", height=400)`
- **Select Box:** `st.selectbox("Label", options=["A", "B"], index=0)`
- **Data Editor:** `st.data_editor(df)` - editable dataframe
- **Forms:** `with st.form("form_key"):` - batch input submission

### Buttons and Actions
- **Button:** `if st.button("Click Me", key="unique_key"):`
- **Form Submit:** `submitted = st.form_submit_button("Submit")`
- **Use unique keys** for all widgets to avoid state conflicts

## API Communication (httpx in stlite)

### Backend Calls
- **Library:** `httpx` (works in Pyodide/stlite)
- **Base URL:** Relative paths work in stlite (same origin as HTML)
- **Example:**
  ```python
  import httpx
  
  # GET request
  response = httpx.get("/api/records", headers=headers, timeout=10.0)
  
  # POST request
  response = httpx.post(
      "/api/records/123",
      json={"lx": "word", "ps": "n"},
      headers=headers,
      timeout=10.0
  )
  ```

### Authentication
- **Token Storage:** `st.session_state.token`
- **Headers:** `{"Authorization": f"Bearer {token}"}`
- **Cookie Setting:** Use JavaScript via `st.markdown` with `unsafe_allow_html=True`
  ```python
  st.markdown(
      f"""
      <div style="display:none">
          <script>
              document.cookie = "session={token}; Max-Age=2592000; path=/; SameSite=Lax";
          </script>
      </div>
      """,
      unsafe_allow_html=True
  )
  ```

## Output Requirements

### Code Structure
1. **Imports at top:** `streamlit`, `httpx`, `os`, `re`, `json`
2. **Page config first:** `st.set_page_config(page_title="...", layout="wide")`
3. **Helper functions:** Define before `main()`
4. **Main function:** Entry point with routing logic
5. **Entry guard:** `if __name__ == "__main__": main()`

### Session State Management
- Initialize all session state keys before use
- Use `if "key" not in st.session_state:` pattern
- Clear state on logout: `del st.session_state.user`

### Error Handling
- Wrap API calls in try/except blocks
- Display errors with `st.error(f"Error: {e}")`
- Show debug info in expanders: `with st.expander("Details"): st.json(data)`

### UI/UX Best Practices
- **Compact layout:** Use `layout="wide"` in page config
- **Sidebar navigation:** Move controls to sidebar to maximize content area
- **Loading indicators:** `with st.spinner("Loading..."):`
- **Success feedback:** `st.success("Saved!")` then `st.rerun()`
- **Consistent spacing:** Use `st.divider()` between sections

## Style Guidelines

### Code Style
- **Minimal imports:** Only import what's needed
- **Clear naming:** `selected_record`, `update_payload`, `auth_headers`
- **Consistent grouping:** Related widgets in same `st.columns()` or `st.container()`
- **Comments:** Only for non-obvious logic (match existing codebase frequency)

### Widget Organization
```python
# Good: Grouped related controls
col_sel, col_btn = st.columns([8, 2])
with col_sel:
    selected = st.selectbox("Record", options)
with col_btn:
    if st.button("Edit"):
        st.rerun()
```

## stlite-Specific Considerations

### Limitations
- **No file system access** (except via browser APIs)
- **No subprocess calls** (pure Python only)
- **Limited stdlib:** Some modules unavailable in Pyodide
- **Async context:** Some operations may need `await` in Pyodide

### Workarounds
- **File uploads:** Use `st.file_uploader()` (works in stlite)
- **Downloads:** Use `st.download_button()` (works in stlite)
- **External data:** Fetch via `httpx` from APIs

### Dependencies
- Declare in `scripts/bundle_stlite.py` requirements list
- Only use packages available in Pyodide: `httpx`, `python-dotenv`
- Check Pyodide package list: https://pyodide.org/en/stable/usage/packages-in-pyodide.html

## Testing Checklist

Before submitting UI changes:
1. ✓ Run `uv run python scripts/bundle_stlite.py`
2. ✓ Open `dist/index.html` in browser
3. ✓ Test all navigation flows
4. ✓ Verify API calls work (check browser console for errors)
5. ✓ Test authentication flow (login/logout)
6. ✓ Verify session persistence across page refreshes
