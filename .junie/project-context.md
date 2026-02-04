<!-- Copyright (c) 2026 Brothertown Language -->

# Project Context and Architecture

## Project Overview

### Identity and Purpose
The SNEA Online Shoebox Editor is a collaborative platform designed for editing Southern New England Algonquian (SNEA) language records.
- **Format:** Records are maintained in the MDF (Multi-Dictionary Formatter) standard, compatible with Shoebox/Toolbox.
- **Languages:** Focuses on Natick, Mohegan-Pequot, Narragansett, and other related SNEA languages.
- **Repository:** The project is maintained in a private repository with restricted access.
- **Ethics:**
    - **Nation Sovereignty:** All work must respect the sovereignty of the SNEA Nations.
    - **Inclusive Language:** Use "Nation" instead of "Tribal" in all documentation and UI.
    - **Attribution:** Clearly mark all AI-assisted contributions.

### Technology Stack
- **Language:** 100% Python.
- **Frontend/Backend:** Streamlit (Server-side execution).
- **Database:** Aiven (PostgreSQL 17.7). Local development uses `pgserver` (PostgreSQL 16.2). All code must be compatible with PostgreSQL 16.2.
- **Authentication:** GitHub OAuth (via `streamlit-oauth`).
- **Package Manager:** `uv` (Mandatory: Do not use `pip` or `poetry`).
- **Deployment:** Streamlit Community Cloud (Auto-deploy on push to `main`).

## Architecture Details

### Application Structure
- **Unified App:** The frontend and backend logic are integrated within the Streamlit application.
- **Legacy Folder Structure:** The `src/frontend/` directory is a legacy artifact. While it might seem redundant in a monolithic structure, it is **mandatory** for Streamlit Community Cloud deployment, which expects the entry point (`app.py`) at this specific path and does not permit changing it.
- **Main Entry Point:** `src/frontend/app.py`
- **Database:** An Aiven PostgreSQL instance serves as the persistent data store.
- **Authentication:** GitHub OAuth is used to manage access for authorized users.

### Data Layer
- **Standard:** Multi-Dictionary Formatter (MDF).
- **Storage:** PostgreSQL (Aiven in Prod, `pgserver` in Dev).
- **Compatibility:** Strictly target PostgreSQL 16.2 features to ensure local/prod alignment.
- **Core Hierarchy:** `\lx` (lexeme) -> `\ps` (part of speech) -> `\ge` (gloss).
- **Validation:**
    - The system provides advisory visual feedback on MDF compliance.
    - Linguists maintain final authority on whether to enforce or deviate from MDF conventions.
- **Key Components:**
    - **Parser:** `src/shared/mdf_parser.py`
    - **Validator:** `src/shared/mdf_validator.py`

## Linguistic Context

### MDF Format Details
- **Common Tags:**
    - `\lx`: Lexeme (the headword).
    - `\ps`: Part of Speech.
    - `\ge`: Gloss (English definition).
    - `\dt`: Date of last update.
- **Structure:** A typical hierarchy is lexeme -> part of speech -> gloss, but the actual structure is flexible and determined by the linguists' needs.
- **Validation:** Visual hints are provided to help maintain consistency, but they are not strictly enforced by the software.

### SNEA Languages Context
- **Family:** Part of the Southern New England Algonquian language family.
- **Documentation:** Work involves both historical records and contemporary documentation efforts.
- **Sensitivity:** Cultural sensitivity and respect for the source Nations are paramount in all technical and linguistic work.
