<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# UI Mocking Description Instructions

To help the AI agent generate or update UI mocks efficiently in `tests/ui/mocks/`, please use the following template to describe the components you need.

## 1. Visual Representation
AI MUST generate a conceptual visual representation of the described UI using **UTF-8 Box-Drawing characters** (e.g., ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ │ ─) and place it at the top of the description file within a `text` code block. This serves as a stable, cross-platform spatial reference for the component layout.

## 2. Description Template

When requesting a mock, try to include these details:

1.  **Component Name & Context**: What is the feature? (e.g., "Record History Sidebar", "Combined View/Edit Tabset").
2.  **Layout Location**: Where does it live? (`st.sidebar` or "Main Panel").
3.  **Visual Elements**: What standard Streamlit elements are involved? (e.g., `st.button`, `st.text_area`, `st.dataframe`).
4.  **Data Requirements**: What fields or mock data structures are needed? (e.g., "Show `timestamp`, `author`, and `change_summary`").
5.  **Composite Logic**: How are elements grouped? (e.g., "An expander for each version containing a `render_mdf_block` and a button").
6.  **Interactions**: What happens when a user interacts? (e.g., "Selecting a version from the sidebar updates the main MDF display").

## 2. Describing Composite Components

Composite components are groups of elements that function together. When describing them:

*   **Nesting**: Specify the container (e.g., "Inside an `st.expander`, show a label and a button").
*   **Repetition**: If the component is a list item, describe one instance (e.g., "A vertical list of 'Record Cards', each showing the lexeme and a status badge").
*   **State Sharing**: Describe how one part of the composite affects another (e.g., "Checking the 'Edit' toggle in the card switches the local MDF display to a text area").

## 3. Example Instruction

> "Create a mock for a **Combined Record View**. 
> - **Sidebar**: Add an 'Editor Mode' toggle.
> - **Main Panel**: 
>   - If 'Editor Mode' is OFF: Show the record using `render_mdf_block`.
>   - If 'Editor Mode' is ON: Show a composite component consisting of a large `st.text_area` for editing the MDF and a 'Save' button below it.
> - **Data**: Use a synthetic record with `lx`, `ps`, and `mdf_data` fields."

## 2. Execution Protocol

Once you provide these instructions, the AI will:
1.  **Draft a design plan**: Detailed markdown description using the template.
2.  **Create/Update a file in `tests/ui/mocks/`** (e.g., `mock_combined_view.py`).
3.  Ensure the mock is runnable via:
    `uv run streamlit run tests/ui/mocks/mock_combined_view.py`
