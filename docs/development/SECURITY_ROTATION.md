<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->

# SNEA Editor Security Rotation Guide

This guide covers the process of rotating secrets if they are accidentally exposed. Use these instructions to revoke compromised keys and restore security.

### Phase 1: Generate New Keys (The "Rotate" Phase)

Follow these links to revoke the old (leaked) keys and generate new ones.

#### 1. GitHub OAuth Client Secret
*Used for user authentication.*

*   **Direct Link:** [https://github.com/settings/developers](https://github.com/settings/developers)
*   **Action:** Click your App name -> **Client secrets** -> **Generate a new client secret**.
*   **Update Secrets**: Update your local `.streamlit/secrets.toml` and the Streamlit Cloud "Secrets" UI.

#### 2. Aiven Database Password
*Used to connect to your PostgreSQL database.*

*   **Action:** Go to your Aiven console -> Select your PostgreSQL service -> **Change password**.
*   **Update Secrets**: Update the `url` in your `.streamlit/secrets.toml` and Streamlit Cloud "Secrets" UI.

### Phase 2: Sync to Production

1.  **Local Sync**: Update `.streamlit/secrets.toml` (which is ignored by git).
2.  **Cloud Sync**: Paste the new secrets into the Streamlit Community Cloud "Secrets" management interface.
