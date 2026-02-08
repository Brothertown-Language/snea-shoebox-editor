<!-- Copyright (c) 2026 Brothertown Language -->

# Project Architecture and Linguistic Context

## 1. Project Overview and Ethics

### IDENTITY AND PURPOSE
The SNEA Online Shoebox Editor is a collaborative platform for editing Southern New England Algonquian (SNEA) language records in MDF format.
- **FOCUS:** Natick, Mohegan-Pequot, Narragansett, and related SNEA languages.
- **ETHICS:** 
    - Respect Nation Sovereignty. 
    - Use "Nation" instead of "Tribal."
    - Clearly mark AI contributions.

### TECH STACK
- **LANGUAGE:** 100% Python.
- **UI:** Streamlit (Server-side execution).
- **DATABASE:** PostgreSQL (Aiven in Prod, `pgserver` in Dev).
- **AUTH:** GitHub OAuth.
- **PACKAGE MANAGER:** `uv` (Mandatory).

---

## 2. Architecture Details

### APPLICATION STRUCTURE
- **UNIFIED APP:** Integrated frontend and backend logic.
- **LEGACY PATH:** `src/frontend/app.py` is the mandatory entry point for Streamlit Cloud.
- **DATA PERSISTENCE:** Aiven PostgreSQL (v17.7 prod, v16.2 dev compatible).

### DATA LAYER (MDF)
- **STANDARD:** Multi-Dictionary Formatter (MDF).
- **CORE HIERARCHY:** `\lx` (Lexeme) -> `\ps` (Part of Speech) -> `\ge` (Gloss).
- **COMPATIBILITY:** Target PostgreSQL 16.2 features for alignment between dev and prod.

---

## 3. Linguistic Context

### MDF TAGS AND STRUCTURE
- `\lx`: Headword.
- `\ps`: Part of Speech.
- `\ge`: English Gloss.
- `\dt`: Date of last update.
- **VALIDATION:** System provides advisory visual hints; linguists have final authority.

### SNEA CONTEXT
- Work involves historical records and contemporary documentation.
- Cultural sensitivity is paramount in all technical and linguistic implementations.
