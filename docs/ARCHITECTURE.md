<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
<!-- Licensed under CC BY-SA 4.0 -->
# SNEA Online Shoebox Editor Architecture

## Overview

The SNEA Online Shoebox Editor is a collaborative, version-controlled platform for editing linguistic data in Multi-Dictionary Form (MDF). It is built using a 100% Python stack and deployed on Streamlit Community Cloud.

## Component Stack

- **Streamlit Application**: [Streamlit](https://streamlit.io/) (Hosted on Streamlit Community Cloud).
  - A unified Python application serves both the frontend and backend logic.
  - Handles UI rendering, authentication, and database interactions.
  - Implements optimistic locking and versioning for concurrent editing.
  - Features a multi-user "Matchup Review" workflow for MDF synchronization.
- **Database**: [Aiven](https://aiven.io/) (PostgreSQL).
  - Persistent PostgreSQL database utilizing standard `ILIKE` and specialized indexing for performance.
  - Supports Many-to-Many relationships for cross-dialectal linguistic records.
  - Integrated ISO 639-3 reference data for language normalization.
- **Authentication**: GitHub OAuth & RBAC.
  - Integrated via GitHub OAuth for secure user identification.
  - Role-Based Access Control (RBAC) mapping GitHub Teams to application roles (Admin, Editor, Viewer).
  - Cookie-based session rehydration for seamless multi-page experience.

## Data Model & Schema Management

The primary data format is MDF (Multi-Dictionary Form).
- **Hierarchy**: `\lx` (Lexeme) -> `\ps` (Part of Speech) -> `\ge` (Gloss English).
- **Language Mapping**: Supports multiple languages per record via a join table, allowing for complex cross-references.
- **Validation**: Advisory visual feedback on MDF compliance; linguists decide whether to enforce.
- **History**: Every change is tracked in an `edit_history` table for full auditability and version control.
- **Automated Schema**: The application manages its own database schema via SQLAlchemy models. On startup, the app automatically creates missing tables and applies necessary updates. No manual SQL execution is required for schema maintenance.

## Deployment Pipeline

- **Continuous Deployment**: Streamlit Community Cloud automatically pulls and builds on push to the main branch.
- **Secrets Management**: Managed via `.streamlit/secrets.toml` locally and the Streamlit Cloud "Secrets" UI in production.

## Directory Structure

- `src/`: Source code for both frontend and backend.
- `docs/`: Technical and linguistic documentation.
- `tests/`: Automated test suite.
- `.junie/`: AI-specific Sparse Priming Representations (SPR) and guidelines.
