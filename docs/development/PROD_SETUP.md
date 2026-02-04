# Infrastructure & Production Setup Guide

This guide provides instructions for setting up the production environment for the SNEA Shoebox Editor.

## 1. Streamlit Community Cloud (Frontend)

The application is hosted on **Streamlit Community Cloud**.

### Organization Repository Access
Since this repository is part of a GitHub Organization, access must be granted at the Organization level:

#### Option A: If you are an Organization Owner
1.  Go to your **Organization Settings** (click your profile picture -> **Your organizations** -> click the gear icon next to your Org).
2.  In the left sidebar, go to **Third-party access** -> **GitHub Apps**.
3.  If **Streamlit** is listed, click **Configure** and ensure it has access to the correct repository.
4.  If it is NOT listed, follow the **Personal Settings** flow below to "Request" access.

#### Option B: Via Personal Settings (Requesting access)
1.  **Direct Link**: Go to [**GitHub Settings > Applications > Authorized GitHub Apps**](https://github.com/settings/applications).
2.  Find **Streamlit** and click **Configure**.
3.  Scroll to **Organization access**.
4.  Find the organization and click **Grant** (or **Request**). 
    - If you click **Request**, an owner must approve it in the "Third-party access" section mentioned above.

### Deployment Settings
- **Main file path**: `src/frontend/app.py`
- **App URL**: `https://snea-edit.streamlit.app`

### Managing Excluded Files
The project contains development-only files (tests, documentation, docker configs) that are not needed in the production app. We manage this using the official Streamlit `server.exclude_pattern` configuration in `.streamlit/config.toml`.

Streamlit Community Cloud uses this pattern to determine which files to ignore during the build and deployment process. Ensure this file is kept up to date with any new development-only artifacts.

Example `.streamlit/config.toml`:
```toml
[server]
exclude_pattern = "docs/**, tests/**, .junie/**, ..."
```

### Verification of Exclusions
The application includes a built-in verification mechanism to ensure that development-only files listed in `server.exclude_pattern` are indeed absent from the production environment. 
- In the **System Status** page of the app, look for the **Deployment Integrity (Exclusion Check)** section.
- On Streamlit Community Cloud, this section should ideally show a success message (✅ All files in `server.exclude_pattern` are successfully excluded).
- During local development, it will show an info message (ℹ️ Development files are present) because these files are necessary for your local workflow.
- **Note**: Essential files like `pyproject.toml` and `uv.lock` must NOT be included in the exclusion check as they are required for deployment.

### Troubleshooting: "Subdomain Taken" Error
If your deployment failed and you now see "Subdomain taken" when trying to re-create it:
1.  **Check your Dashboard**: Go to [share.streamlit.app](https://share.streamlit.app). The failed app is likely already in your list.
2.  **Fix or Delete**: 
    - Click the three dots (⋮) -> **Settings** -> **Configuration** to fix the **Main file path** to `src/frontend/app.py`.
    - Alternatively, delete the failed app and wait 5 minutes before trying to use the same subdomain again.

## 2. Supabase (Database)

The database is hosted on **Supabase (PostgreSQL)**.

## 3. GitHub OAuth (Authentication)

Authentication is handled via **GitHub OAuth** integrated into the Streamlit application.
