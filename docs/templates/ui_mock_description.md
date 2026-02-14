<!-- Copyright (c) 2026 Brothertown Language -->
# UI Mock Description Template

## 1. Visual Mock

```text
┌───────────────────────────┬──────────────────────────────────────────────────┐
│ [Component Name]          │  [Main View]                                     │
├───────────────────────────┼──────────────────────────────────────────────────┤
│                           │                                                  │
│  [Element 1]              │  ┌────────────────────────────────────────────┐  │
│  [ ( ) Select ]           │  │ [Specialized Content]                      │  │
│                           │  └────────────────────────────────────────────┘  │
└───────────────────────────┴──────────────────────────────────────────────────┘
```

## 2. Component Name & Context
**Name**: [e.g., Record View/Edit]
**Context**: [What is the primary goal of this feature?]

## 2. Layout Location
**Location**: [e.g., Sidebar, Main Panel, or specific Container]

## 3. Visual Elements
**Functional UI Components**:
- [ ] Action Buttons (triggers)
- [ ] Single-line Text Input
- [ ] Multi-line Text Editor
- [ ] Dropdown Selector (single/multi)
- [ ] Data Display Table
- [ ] Specialized Content Renderer (e.g., MDF)
- [ ] Collapsible Detail Section
- [ ] Other: [specify]

## 4. Data Requirements
**Mock Data**:
- [ ] Fields: [e.g., lx, ps, ge, fulltext]
- [ ] Source collections: [e.g., Natick, Mohegan, SNEA-General]
- [ ] User Permissions: [e.g., viewer, editor, admin]

## 5. Composite Logic
**Grouping & Containers**:
- [e.g., "Main record view uses a container with the MDF block renderer followed by an action button row."]

## 6. Interactions & State
**Behavior**:
- [e.g., "Clicking 'Edit' switches the display to a text area."]
- [e.g., "Sidebar search filters the records displayed in the main panel."]
