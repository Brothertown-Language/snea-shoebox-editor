<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
<!-- Licensed under CC BY-SA 4.0 -->

# SNEA Shoebox Editor - Functional Requirements

This document outlines the required features and specialized interfaces for the SNEA Shoebox Editor.

## 1. Administrative Editors

### 1.1 Source Editor
A dedicated administrative interface must be provided for managing the `sources` table. 
- **Purpose**: To allow authorized users to add, update, or remove source collections (e.g., "Natick/Trumbull").
- **Independence**: This is a standalone administrative tool, separate from the primary linguistic MDF record editor.
- **Fields**: Name (unique), Description, and Citation Format (optional).

## 2. Main Editor
(To be detailed as we finalize the `records` table requirements...)

## 3. MDF Standards & Conventions

### 3.1 Cross-References
To maintain MDF parity while supporting multiple source references, the following convention is used:
- **Tag**: `\cf` (Compare/Cross-reference)
- **Format**: All external source references within the `\cf` tag must be prefixed with `Also: ` to distinguish them from standard linguistic cross-references.
- **Example**: `\cf Also: Modern Mohegan Dictionary, p. 42`
