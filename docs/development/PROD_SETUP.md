# Infrastructure & Production Setup Guide

This guide provides instructions for setting up the production environment for the SNEA Shoebox Editor.

## 1. Streamlit Community Cloud (Frontend)

The application is hosted on **Streamlit Community Cloud**.

### Organization Repository Access
Since this repository is part of a GitHub Organization, you must grant Streamlit access to the organization's repositories:

1.  **Direct Link**: Go to [**GitHub Settings > Applications > Authorized GitHub Apps**](https://github.com/settings/applications).
    - *Alternatively*: Click your profile picture -> **Settings** -> **Applications** (in the left sidebar) -> **Authorized GitHub Apps**.
2.  Find **Streamlit** in the list and click **Configure**.
3.  Scroll down to the **Organization access** section.
4.  Find your organization (e.g., `Brothertown-Language`) and click **Grant**.
    - If you are not an owner, click **Request**; an admin must then approve it in the organization settings.
5.  Once granted, the repository will be available in the "Create app" list on [Streamlit Community Cloud](https://share.streamlit.app/).

### Deployment Settings
- **Main file path**: `src/frontend/app.py`
- **App URL**: `https://snea-edit.streamlit.app`

## 2. Supabase (Database)

The database is hosted on **Supabase (PostgreSQL)**.

## 3. GitHub OAuth (Authentication)

Authentication is handled via **GitHub OAuth** integrated into the Streamlit application.
