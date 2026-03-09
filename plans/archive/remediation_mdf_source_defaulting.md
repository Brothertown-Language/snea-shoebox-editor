# Remediation Plan: Require Manual Selection of Source for MDF Upload

## Problem Statement
The MDF upload feature currently defaults the "Target source collection" to the user's GitHub username if it exists as a Source in the database. This automated selection can lead to workflow issues where entries are accidentally uploaded to the wrong source if the user doesn't notice the default.

## Proposed Changes

### 1. `src/frontend/pages/upload_mdf.py`
- **Modify Default Selection**: Remove the logic that attempts to match the current user's email/GitHub username to a source.
- **Set Placeholder as Default**: Ensure the `SELECT_SOURCE_LABEL` ("Select a source...") is the default index for the `st.selectbox`.
- **Enforce Selection**: The "Upload & Review" button (further down in the file, likely around line 130-150) must be disabled or show an error if `selected_source` is `SELECT_SOURCE_LABEL`.

## Verification Steps
1. Navigate to the MDF Upload page.
2. Verify that "Target source collection" defaults to "Select a source...".
3. Verify that the "Upload & Review" button is either disabled or correctly prompts for a selection if the placeholder is active.
4. Verify that selecting a valid source enables the upload process.
5. Verify that adding a new source (inline) still works and correctly selects the newly created source after creation.

## Approval Required
- [ ] Go
- [ ] Proceed
- [ ] Approved
