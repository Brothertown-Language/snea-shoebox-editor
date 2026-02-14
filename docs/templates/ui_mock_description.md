<!-- Copyright (c) 2026 Brothertown Language -->
# UI Mock Description Template

Use this template to describe a new UI mock or updates to an existing one.

## 1. Component Name & Context
**Name**: [e.g., Record View/Edit]
**Context**: [What is the primary goal of this feature?]

## 2. Layout Location
**Location**: [e.g., `st.sidebar`, Main Panel, or specific `st.container`]

## 3. Visual Elements
**Streamlit Elements**:
- [ ] `st.button`
- [ ] `st.text_area` / `st.text_input`
- [ ] `st.selectbox` / `st.multiselect`
- [ ] `st.dataframe` / `st.table`
- [ ] `render_mdf_block()` (custom)
- [ ] Other: [specify]

## 4. Data Requirements
**Mock Data**:
- [ ] Fields: [e.g., lx, ps, ge, fulltext]
- [ ] Source collections: [e.g., Natick, Mohegan, SNEA-General]
- [ ] User Permissions: [e.g., viewer, editor, admin]

## 5. Composite Logic
**Grouping & Containers**:
- [e.g., "Main record view uses an `st.container` with `render_mdf_block` followed by an action button row."]

## 6. Interactions & State
**Behavior**:
- [e.g., "Clicking 'Edit' switches the display to an `st.text_area`."]
- [e.g., "Sidebar search filters the records displayed in the main panel."]
