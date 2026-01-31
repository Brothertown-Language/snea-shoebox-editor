<!-- Copyright (c) 2026 Brothertown Language -->
# SNEA Online Shoebox Editor Architecture

## Overview

The SNEA Online Shoebox Editor is a collaborative, version-controlled platform for editing linguistic data in Multi-Dictionary Form (MDF). It is built using a 100% Python stack and deployed on Cloudflare's edge infrastructure.

## Component Stack

- **Frontend**: [Solara](https://solara.dev/) (Reactive Python UI).
  - Compiled to WebAssembly (WASM) via Pyodide.
  - State management is reactive, ensuring a modern web experience without JavaScript.
- **Backend**: [Cloudflare Workers](https://workers.cloudflare.com/) (Python runtime).
  - Handles API requests, authentication, and database interactions.
  - Implements optimistic locking for concurrent editing.
- **Database**: [Cloudflare D1](https://developers.cloudflare.com/d1/).
  - SQL database at the edge.
  - Stores linguistic records and edit history.
- **Authentication**: GitHub OAuth.
  - Access is restricted to specific GitHub organizations/teams (e.g., `Brothertown-Language`).

## Data Model & Schema Management

The primary data format is MDF (Multi-Dictionary Form).
- **Hierarchy**: \lx (Lexeme) -> \ps (Part of Speech) -> \ge (Gloss English).
- **Validation**: Strict parity with MDF standards is enforced at the entry point.
- **History**: Every change is tracked in an `edit_history` table for full auditability and version control.
- **Automated Schema**: The application is responsible for its own database schema. On startup, the app automatically creates missing tables and applies necessary `ALTER` statements to existing tables. No manual SQL execution is required for schema maintenance.

## Deployment Pipeline

- **CI/CD**: GitHub Actions + Wrangler.
- **"Zero-Touch"**: The environment is designed so that deployment requires no local configuration beyond initial bootstrapping.
- **Secrets**: Managed via GitHub Actions secrets, populated by the `bootstrap_env.py` script.

## Directory Structure

- `src/`: Source code for both frontend and backend.
- `docs/`: Technical and linguistic documentation.
- `tests/`: Automated test suite.
- `.junie/`: AI-specific Sparse Priming Representations (SPR) and guidelines.
