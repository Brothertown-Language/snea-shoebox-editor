<!-- Copyright (c) 2026 Brothertown Language -->
# UI Mock Description: Records View

## 1. Visual Mock

```text
┌───────────────────────────┬──────────────────────────────────────────────────┐
│ Records (Sidebar)         │  Records List                                    │
├───────────────────────────┼──────────────────────────────────────────────────┤
│                           │  ┌────────────────────────────────────────────┐  │
│  Search                   │  │ \lx example 1                              │  │
│  [ Enter text...      ]   │  │ \ps n                                      │  │
│                           │  │ \ge translation 1                          │  │
│  Search Mode              │  └────────────────────────────────────────────┘  │
│  (●) Lexeme  ( ) FTS      │  [<] [>] [Copy Plain] [Copy Rich] [Add] [x] [✎]  │
│                           │                                                  │
│  Source Collection        │  ┌────────────────────────────────────────────┐  │
│  [ Mohegan          ▾ ]   │  │ \lx example 2                              │  │
│                           │  │ \ps v                                      │  │
│  Pagination               │  │ \ge translation 2                          │  │
│  [< Prev] [Next >]        │  └────────────────────────────────────────────┘  │
│  Page 1 of 10             │  [<] [>] [Copy Plain] [Copy Rich] [Add] [x] [✎]  │
│  Size: [ 25 ▾ ]           │                                                  │
│ ┌───────────────────────┐ │                                                  │
│ │ Download Cart         │ │                                                  │
└───────────────────────────┴──────────────────────────────────────────────────┘
```

## 2. Component Name & Context
**Name**: Records
**Slug**: `records`
**Context**: Primary interface for users to discover, view, edit, and manage records in a paginated list view. Supports both high-level search and granular record editing across multiple records simultaneously (via expansion), including a "shopping cart" for MDF exports. Optimized for large datasets (10,000+ records) using server-side pagination.

## 2. Layout Location
**Location**: 
- **Main Panel**: Primary record display and edit area.
- **Sidebar**: All navigation, search filters, source switching, and download cart status.

## 3. Visual Elements
**Functional UI Components**:
- **Sidebar Area**:
    - Single-line Text Input ("Search")
    - Search Mode Toggle ("Lexeme" vs "Fulltext Search (FTS)")
    - Dropdown Selector ("Source Collection": All Sources, or specific source)
    - **Pagination Controls**:
        - Previous/Next Page buttons.
        - Page Number display ("Page X of Y").
        - Page Size Selector ("Results per page").
- **Main Display Area**:
    - **Record Card List**: A vertical sequence of individual record containers.
    - Specialized MDF Renderer (displays the record in MDF format with optional structural highlighting)
    - Multi-line Text Editor (visible only in Edit Mode for a specific record)
    - Edit Actions: `[Save]`, `[Cancel]` (visible only in Edit Mode; positioned immediately below the Text Editor)
    - Action Toolbar: `[<]`, `[>]`, `[Copy Plain]`, `[Copy Rich]`, `[Add to Cart]`, `[edit]` (conditional), `[delete]` (conditional) (consolidated per record)
    - Preference Toggle: "Structural Highlighting" checkbox/toggle
    - Collapsible Detail Section ("Revision History")
    - **Revision History Detail**:
        - Lazy-loaded previous version display.
        - Highlighted Diff (comparing current record with previous version).
        - "Restore to Editor" action (conditional on Edit Mode).
- **Status & Notifications**:
    - Information Panel in Sidebar (Download Cart summary: "X records from Y sources")
    - Cart Action Buttons: `[Download]`, `[Discard]`

## 4. Data Requirements
**Mock Data**:
- **Records**: Synthetic MDF records containing common tags: `\lx`, `\ps`, `\ge`, `\inf`.
- **Sources**: At least three distinct mock sources (e.g., "Natick", "Mohegan", "SNEA-General").
- **User Roles**: A toggle or state variable for "Viewer" vs "Editor" permissions.

## 5. Composite Logic
**Grouping & Containers**:
- **Record Card Component**: A repeatable container for a single record.
    - Includes the MDF Renderer or Multi-line Text Editor.
    - Includes the Action Toolbar and Revision History specific to that record.
- **Display/Edit Container**: A logical group wrapping the MDF Renderer (View Mode) or Multi-line Text Editor (Edit Mode) within a Record Card. 
    - In **View Mode**, it includes the MDF Renderer and the Action Toolbar.
    - In **Edit Mode**, it replaces the MDF Renderer with the Multi-line Text Editor and adds `[Save]` / `[Cancel]` buttons immediately below it.
- **Cart Summary Widget**: A dedicated functional block in the sidebar summarizing tagged records, including `[Download]` and `[Discard]` actions.
- **Pagination Widget**: A composite control in the sidebar for navigating pages.

## 6. Interactions & State
**Behavior**:
- **Multi-Record Viewing**: Multiple records are displayed simultaneously in a scrollable list.
- **Pagination**:
    - Records are loaded in batches based on "Results per page" (e.g., 10, 25, 50, 100).
    - **Lazy Loading**: Only the records for the current page are fetched from the database (simulated in mock) and rendered in the UI.
    - Page size preference is persisted in `UserPreference`.
    - Navigating between pages updates the record set without reloading the entire page.
- **View-Only Mode (Default)**: Records are displayed using the specialized MDF Renderer within their respective cards. 
- **Structural Validation Highlighting**:
    - The renderer automatically identifies lines that violate the standard MDF hierarchy (`\lx` -> `\ps` -> `\ge`) or contain unknown tags.
    - Problematic lines are visually highlighted (e.g., subtle red background or warning icon).
    - **Toggleability**: Structural highlighting can be toggled on/off via a "Structural Highlighting" checkbox. 
    - **Persistence**: The toggle state is persisted in the database as the user's default preference for the `records` view.
- **Copy to Clipboard**:
    - `[Copy Plain]`: Copies the raw MDF text of the record to the system clipboard.
    - `[Copy Rich]`: Copies the record with structural highlighting applied (simulated in mock as a success notification).
- **Edit Mode Transition**: Clicking the record view or the `[edit]` action button (if user has edit permissions) replaces the MDF Renderer with the Multi-line Text Editor and reveals the `[Save]` / `[Cancel]` buttons.
- **Search & Filtering**: 
    - The Search Mode Toggle determines whether the text input filters by the primary lexeme field (`\lx`) or performs a full-text search (FTS) across all MDF tags.
    - Updating search terms, toggling the search mode, or changing the source dropdown in the sidebar immediately filters the navigable record set.
- **Permission-Gated Elements**: `[edit]` and `[delete]` action buttons are only rendered if the user session has "Editor" permissions.
- **Download Cart Logic**: 
    - `[Add to Cart]` appends the current record to a persistent tracking list.
    - `[Download]` triggers the export process (bundled zip if multiple sources).
    - `[Discard]` clears all records from the current cart session.
    - If records from multiple sources are in the cart, the system indicates that exports will be bundled in a zip archive.
- **Record Navigation**: "Next/Previous" actions update the currently displayed record index based on the active search/source filters.
- **Layout Consistency**: The view applies standard 1rem horizontal padding for the main panel to maintain project-wide alignment.
- **Revision History & Versioning**:
    - Expanding "Revision History" shows a list of past edits (simulated).
    - **Lazy Loading**: Selecting a version (or clicking "Compare with Previous") triggers a lazy-load simulation (e.g., spinner) to fetch the full historical MDF.
    - **Diff Visualization**: Differences between the current version and the selected historical version are highlighted using linguistic-optimized gutter icons. Contiguous changes (a deletion followed by an addition) are grouped and marked with a blue `→` (Transformation) icon. Isolated deletions are marked with a red `×` icon, and isolated additions with a green `+` icon. The visualization uses large, clear icons (gutter-based) and ultra-tight line spacing (`line-height: 1.0`), following the standardized line indicator pattern. Indicators are separated from the intact record content.
    - **Restore to Editor**: If the record card is currently in Edit Mode, a "Restore to Editor" button appears in the history detail. Clicking it overwrites the current content in the `Multi-line Text Editor` with the historical version, allowing the user to resume editing from that state.
- **URL Parameter Tracking (Bookmarking)**:
    - The view tracks critical state parameters (e.g., `search`, `search_mode`, `source`, `page`, `page_size`) in the URL query string.
    - This enables users to bookmark specific search results or share a direct link that reconstructs the exact view state for others.
