<!-- Copyright (c) 2026 Brothertown Language -->
# UI Mock Description: Records View

## 1. Visual Mock

```text
┌───────────────────────────┬──────────────────────────────────────────────────┐
│ Records (Sidebar)         │  Record View                                     │
├───────────────────────────┼──────────────────────────────────────────────────┤
│                           │                                                  │
│  Search                   │  ┌────────────────────────────────────────────┐  │
│  [ Enter text...      ]   │  │ \lx example                                │  │
│                           │  │ \ps n                                      │  │
│  Search Mode              │  │ \ge translation                            │  │
│  (●) Lexeme  ( ) FTS      │  │ \inf examples                              │  │
│                           │  └────────────────────────────────────────────┘  │
│  Source Collection        │                                                  │
│  [ Mohegan          ▾ ]   │  ┌────────────────────────────────────────────┐  │
│                           │  │ [Copy Plain]  [Copy Rich]                  │  │
│  Navigation               │  ├────────────────────────────────────────────┤  │
│  [ Prev ]    [ Next ]     │  │ [Add to Cart]      [edit]      [delete]    │  │
│                           │  └────────────────────────────────────────────┘  │
│  Jump to Record #         │                                                  │
│  [ 42                 ]   │  [ ] Structural Highlighting                     │
│                           │                                                  │
│                           │  ▶ Revision History                              │
│                           │                                                  │
├───────────────────────────┤                                                  │
│ ┌───────────────────────┐ │                                                  │
│ │ Download Cart         │ │                                                  │
│ │ 12 records            │ │                                                  │
│ │                       │ │                                                  │
│ │ [Download] [Discard]  │ │                                                  │
│ └───────────────────────┘ │                                                  │
└───────────────────────────┴──────────────────────────────────────────────────┘

(Edit Mode Main Panel)
┌──────────────────────────────────────────────────┐
│  Editing Record...                               │
├──────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────┐  │
│  │ \lx example|                               │  │
│  │ \ps n                                      │  │
│  │ \ge translation                            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  [ Save ]    [ Cancel ]                          │
└──────────────────────────────────────────────────┘
```

## 2. Component Name & Context
**Name**: Records
**Slug**: `records`
**Context**: Primary interface for users to discover, view, edit, and manage records. Supports both high-level search and granular record editing, including a "shopping cart" for MDF exports.

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
    - Numeric Index Input ("Jump to Record #")
    - Navigation Action Buttons ("Previous", "Next")
- **Main Display Area**:
    - Specialized MDF Renderer (displays the record in MDF format with optional structural highlighting)
    - Horizontal Action Button Group: `[Add to Cart]`, `[edit]` (conditional), `[delete]` (conditional)
    - Copy Action Group: `[Copy Plain]`, `[Copy Rich]`
    - Preference Toggle: "Structural Highlighting" checkbox/toggle
    - Multi-line Text Editor (visible only in Edit Mode)
    - Collapsible Detail Section ("Revision History")
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
- **Display Container**: A logical group wrapping the MDF Renderer and the Horizontal Action Button Group. Record history is accessible via the "Revision History" collapsible section below.
- **Edit Container**: A logical group containing the Multi-line Text Editor for editing, with `[Save]` and `[Cancel]` action buttons positioned below it.
- **Cart Summary Widget**: A dedicated functional block in the sidebar summarizing tagged records, including `[Download]` and `[Discard]` actions.

## 6. Interactions & State
**Behavior**:
- **View-Only Mode (Default)**: Record is displayed using the specialized MDF Renderer. 
- **Structural Validation Highlighting**:
    - The renderer automatically identifies lines that violate the standard MDF hierarchy (`\lx` -> `\ps` -> `\ge`) or contain unknown tags.
    - Problematic lines are visually highlighted (e.g., subtle red background or warning icon).
    - **Toggleability**: Structural highlighting can be toggled on/off via a "Structural Highlighting" checkbox. 
    - **Persistence**: The toggle state is persisted in the database as the user's default preference for the `records` view.
- **Copy to Clipboard**:
    - `[Copy Plain]`: Copies the raw MDF text of the record to the system clipboard.
    - `[Copy Rich]`: Copies the record with structural highlighting applied (simulated in mock as a success notification).
- **Edit Mode Transition**: Clicking the `[edit]` action button replaces the display container with the edit container.
- **Search & Filtering**: 
    - The Search Mode Toggle determines whether the text input filters by the primary lexeme field (`\lx`) or performs a full-text search (FTS) across all MDF tags.
    - Updating search terms, toggling the search mode, or changing the source dropdown in the sidebar immediately filters the navigable record set.
- **Permission-Gated Elements**: `[edit]` and `[delete]` action buttons are only rendered if the user session has "Editor" permissions.
- **Download Cart Logic**: 
    - `[Add to Cart]` appends the current record to a persistent tracking list.
    - `[Download]` triggers the export process (bundled zip if multiple sources).
    - `[Discard]` clears all records from the current cart session.
    - If records from multiple sources are in the cart, the system indicates that exports will be bundled in a zip archive.
- **Record Navigation**: "Jump to Record" and "Next/Previous" actions update the currently displayed record index based on the active search/source filters.
