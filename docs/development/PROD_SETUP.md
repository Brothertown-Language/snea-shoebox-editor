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

## 2. Supabase (Database)

The database is hosted on **Supabase (PostgreSQL)**.

## 3. GitHub OAuth (Authentication)

Authentication is handled via **GitHub OAuth** integrated into the Streamlit application.
