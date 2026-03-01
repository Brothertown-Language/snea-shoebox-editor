# Plan: Remediation of MDF \ln Tag Misuse

## 1. Overview
The `\ln` tag is currently misused in the project as "Language Name" for an entire record, which contradicts the official MDF 1.9a documentation where it is defined as "lexical function (national gloss)". This plan outlines the steps to align the project with the official MDF standard by transitioning to the `\so` (Source of Data) tag for record-level dialect/language identification and `\va`+`\ve` for variant-level marking.

## 2. Documentation Updates 🔄
- **File**: `docs/mdf/mdf-tag-reference.md`
- **Actions**:
    - Update the "Suggested Hierarchy" section to remove `\ln` as a primary marker and promote `\so`.
    - Correct the definition of `\ln` in the "Tag Reference" section to match the official MDF 1.9a standard.
    - Update the "Dialect and Multi-lingual Data" section to recommend the `\so` and `\va`+`\ve` approach.
    - Add a "Legacy/Migration Note" about the previous misuse of `\ln`.
- **File**: `src/mdf/mdf_tags_metadata.json`
- **Actions**:
    - Ensure the `\ln` description matches the official "lexical function (national gloss)".
    - Ensure the `\so` description highlights its role in identifying the dialect/origin of the record.

## 3. Validator Remediation 🔄
- **File**: `src/mdf/validator.py`
- **Actions**:
    - Add `\ln` to the `LEGACY_TAG_MAPPING` as a "misused" or "discouraged" tag when used as a top-level language marker.
    - Suggest `\so` or `\va`+`\ve` as alternatives in the diagnostic message.
    - (Optional) Update `REQUIRED_HIERARCHY` if `\so` should be encouraged over the previous (incorrect) `\ln` requirement.

## 4. Codebase Audit & Data Remediation ⏳
- **Step 1**: Search for all occurrences of `\ln` in the database or source MDF files.
- **Step 2**: Create a report of records that rely on `\ln` for language identification.
- **Step 3**: Develop a transformation script (or manual process) to:
    - Move top-level `\ln` data to `\so` (appending to existing `\so` if necessary).
    - Move variant-level `\ln` data to `\ve` (bundled with `\va`).
- **Step 4**: Verify that the front-end (Streamlit) filters and rendering still function correctly with the new `\so` based identification.

## 5. Verification ✅
- Direct inspection of updated documentation.
- Run `MDFValidator` against test records with both the old `\ln` and new `\so` patterns to verify diagnostic messages.
- Verify that the Mohegan-Pequot examples follow the new official standard.

---
**Status**: ⏳ Pending Approval
