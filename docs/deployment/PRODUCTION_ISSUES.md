# Production Deployment Issues Report

This document tracks technical issues identified during code audits that impact the stability, scalability, and security of the SNEA Shoebox Editor in a production environment.

**Instructions for Maintenance:**
- Remove items from this list only after the fix has been verified in a production-like environment.
- Use the following severity levels:
    - **Critical**: Will cause application crashes, data loss, or severe security breaches.
    - **Major**: Significant performance degradation or core functionality failure under load.
    - **Minor**: UI/UX polish, non-critical performance issues, or edge-case bugs.

---

## 1. Critical Issues

### 1.1 Out-of-Memory (OOM) Risk in MDF Processing
- **Location**: `src/services/upload_service.py` (`suggest_matches`, `assign_homonym_numbers`)
- **Description**: 
    - `suggest_matches`: Loads all lexemes and IDs for the target source into memory to perform matching.
    - `assign_homonym_numbers`: Loads and splits the entire uploaded file/batch into memory to detect intra-batch homonyms.
- **Impact**: As the database grows or upload batch sizes increase, these operations will exhaust server memory, causing the Streamlit application to crash.
- **Recommendation**: Implement batch processing or use targeted SQL queries (e.g., `EXISTS`) instead of loading full result sets for cross-referencing.

---

## 2. Minor Issues

### 2.1 Sensitive Information Exposure in Error Messages
- **Location**: Various `st.error(f"... {e}")` calls in frontend pages and services.
- **Description**: Raw exception messages (containing database internal details, file paths, or API URLs) are displayed directly to the user.
- **Impact**: Minor security risk and poor UX.
- **Recommendation**: Implement a centralized error-handling utility that logs the full exception and shows a user-friendly, sanitized message in the UI.
