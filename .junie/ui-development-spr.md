<!-- Copyright (c) 2026 Brothertown Language -->
# SNEA Editor UI Development Guidelines

## CRITICAL: Regular Streamlit (Streamlit Community Cloud)

### Architecture Requirements
- **Production:** Streamlit Community Cloud (connected to private GitHub repo)
- **Local Development:** Regular Streamlit server (`uv run streamlit run src/frontend/app.py`)
- **NO stlite/WebAssembly** - We use a standard Streamlit execution model.
- **Deployment:** Auto-deploy via git push to main branch.
- **Runtime:** Server-side Python execution (Streamlit Cloud).

### Testing UI Changes
```bash
# Run locally
uv run streamlit run src/frontend/app.py
```

## Framework Specifics (Standard Streamlit)

### State Management
- **Session State:** `st.session_state` - persists across reruns within a user's session.
- **Example:**
  ```python
  if "user" not in st.session_state:
      st.session_state.user = None
  ```

### Database Connection (Aiven)
- **Library:** `st.connection("postgresql", type="sql")`
- **Secrets:** Configure in `.streamlit/secrets.toml` locally or "Secrets" UI in Cloud.
- **Example:**
  ```python
  conn = st.connection("postgresql", type="sql")
  df = conn.query("SELECT * FROM records LIMIT 10;", ttl="10m")
  ```

### Authentication (GitHub OAuth)
- **Library:** `streamlit-oauth`
- **Setup:** Configure `github_oauth` section in secrets.
- **Example:**
  ```python
  from streamlit_oauth import OAuth2Component
  
  oauth2 = OAuth2Component(
      client_id=st.secrets["github_oauth"]["client_id"],
      client_secret=st.secrets["github_oauth"]["client_secret"],
      ...
  )
  ```

### Navigation
- **Query Parameters:** `st.query_params` - URL-based routing.
  ```python
  st.query_params["view"] = "edit"
  current_view = st.query_params.get("view", "list")
  ```
- **Rerun:** `st.rerun()` - trigger full page refresh.

### Input Widgets
- **Text Input:** `st.text_input("Label", value="default")`
- **Text Area:** `st.text_area("Label", value="", height=400)`
- **Select Box:** `st.selectbox("Label", options=["A", "B"], index=0)`
- **Data Editor:** `st.data_editor(df)` - editable dataframe.
- **Forms:** `with st.form("form_key"):` - batch input submission.

### Layout Components
- **Columns:** `st.columns([2, 1, 4, 1])` - proportional width layout.
- **Containers:** `st.container()` - group elements.
- **Tabs:** `st.tabs(["Tab1", "Tab2"])` - tabbed interface.
- **Expander:** `st.expander("Details")` - collapsible sections.
- **Sidebar:** `st.sidebar` - persistent side navigation.

## Output Requirements

### Code Structure
1. **Imports at top:** `streamlit`, `sqlalchemy`, `streamlit_oauth`, etc.
2. **Page config first:** `st.set_page_config(page_title="...", layout="wide")`
3. **Initialize Connection:** `conn = st.connection("postgresql", type="sql")`
4. **Helper functions:** Define before `main()`
5. **Main function:** Entry point with auth and routing logic.
6. **Entry guard:** `if __name__ == "__main__": main()`

### Error Handling
- Wrap database and OAuth calls in try/except blocks.
- Display errors with `st.error(f"Error: {e}")`
- Show debug info in expanders: `with st.expander("Details"): st.write(data)`

## Style Guidelines

### Code Style
- **Minimal imports:** Only import what's needed.
- **Clear naming:** `selected_record`, `update_payload`, `auth_headers`.
- **Consistent grouping:** Related widgets in same `st.columns()` or `st.container()`.

## Testing Checklist

Before submitting UI changes:
1. ✓ Run `uv run streamlit run src/frontend/app.py`
2. ✓ Test all navigation flows.
3. ✓ Verify database operations work (CRUD).
4. ✓ Test authentication flow (login/logout).
5. ✓ Verify session state persistence.
