<!-- Copyright (c) 2026 Brothertown Language -->
# UI Mock Description: View/Edit Record Interface

## 1. Component Name & Context
**Name**: View/Edit Record Interface
**Context**: Primary interface for users to discover, view, edit, and manage records. Supports both high-level search and granular record editing, including a "shopping cart" for MDF exports.

## 2. Layout Location
**Location**: 
- **Main Panel**: Primary record display and edit area.
- **Sidebar**: All navigation, search filters, source switching, and download cart status.

## 3. Visual Elements
**Streamlit Elements**:
- `st.sidebar`:
    - `st.text_input` ("Search")
    - `st.radio` ("Search Type": Lexeme, Fulltext)
    - `st.selectbox` ("Source Collection": All Sources, or specific source)
    - `st.number_input` ("Jump to Record #")
    - `st.button` ("Previous", "Next")
- `Main Panel`:
    - `render_mdf_block()` (displays the record in MDF format)
    - **Action Row** (Buttons): `[view edits]`, `[Add to Cart]`, `[edit]` (conditional), `[delete]` (conditional)
    - `st.text_area` (MDF Editor - visible only in Edit Mode)
    - `st.expander` ("Revision History")
- `Status`:
    - `st.sidebar.info` (Download Cart summary: "X records from Y sources")

## 4. Data Requirements
**Mock Data**:
- **Records**: Synthetic MDF records containing common tags: `\lx`, `\ps`, `\ge`, `\inf`.
- **Sources**: At least three distinct mock sources (e.g., "Natick", "Mohegan", "SNEA-General").
- **User Roles**: A toggle or state variable for "Viewer" vs "Editor" permissions.

## 5. Composite Logic
**Grouping & Containers**:
- **Display Block**: An `st.container` wrapping the `render_mdf_block()` and the horizontal action button row.
- **Edit Block**: An `st.container` containing the `st.text_area` for editing, with `[Save]` and `[Cancel]` buttons positioned below it.
- **Cart Widget**: A dedicated section in the sidebar summarizing tagged records.

## 6. Interactions & State
**Behavior**:
- **View Mode (Default)**: Record is displayed using `render_mdf_block()`.
- **Edit Mode**: Clicking `[edit]` replaces the display block with the edit block.
- **Search & Filter**: Changing search terms or source selection in the sidebar immediately filters the record navigation set.
- **Permissions**: `[edit]` and `[delete]` buttons are only rendered if the user state is "Editor".
- **Download Cart**: 
    - `[Add to Cart]` appends the record to a session-state list.
    - If multiple sources are present in the cart, the system acknowledges that exports will be zipped.
- **Navigation**: "Jump to Record" and "Next/Previous" update the currently displayed record index based on the active filter.
