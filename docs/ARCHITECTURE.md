<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# SNEA Online Shoebox Editor Architecture

## Overview

The SNEA Online Shoebox Editor is a collaborative, version-controlled platform for editing linguistic data in Multi-Dictionary Form (MDF). It is built using a 100% Python stack and deployed on Streamlit Community Cloud.

## Component Stack

- **Streamlit Application**: [Streamlit](https://streamlit.io/) (Hosted on Streamlit Community Cloud).
  - A unified Python application serves both the frontend and backend logic.
  - Handles UI rendering, authentication, and database interactions.
  - Implements optimistic locking for concurrent editing. (Pending)
  - Implemented: Basic record viewing, automatic schema initialization.
- **Database**: [Aiven](https://aiven.io/) (PostgreSQL).
  - Persistent PostgreSQL database.
  - Stores linguistic records and edit history.
  - Implemented tables: `sources`, `records`.
  - Pending tables: `users`, `edit_history`, `permissions`, `embeddings`.
- **Authentication**: GitHub OAuth.
  - Integrated via `streamlit-oauth`.
  - Access can be restricted to specific GitHub organizations/teams.

## Data Model & Schema Management

The primary data format is MDF (Multi-Dictionary Form).
- **Hierarchy**: \lx (Lexeme) -> \ps (Part of Speech) -> \ge (Gloss English).
- **Validation**: Advisory visual feedback on MDF compliance; linguists decide whether to enforce.
- **History**: Every change is tracked in an `edit_history` table for full auditability and version control.
- **Automated Schema**: The application is responsible for its own database schema. On startup, the app automatically creates missing tables and applies necessary `ALTER` statements to existing tables. No manual SQL execution is required for schema maintenance.

## Deployment Pipeline

- **Continuous Deployment**: Streamlit Community Cloud automatically pulls and builds on push to the main branch.
- **Secrets Management**: Managed via `.streamlit/secrets.toml` locally and the Streamlit Cloud "Secrets" UI in production.

## Directory Structure

- `src/`: Source code for both frontend and backend.
- `docs/`: Technical and linguistic documentation.
- `tests/`: Automated test suite.
- `.junie/`: AI-specific Sparse Priming Representations (SPR) and guidelines.
