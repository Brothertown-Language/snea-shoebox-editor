# Infrastructure & Production Setup Guide

This guide provides instructions for setting up the production environment for the SNEA Shoebox Editor.

## 1. Streamlit Community Cloud (Frontend)

The application is hosted on **Streamlit Community Cloud**.

### Organization Repository Access
Since this repository is part of a GitHub Organization, you must grant Streamlit access to the organization's repositories:

1.  Go to your GitHub [**Settings > Applications > Authorized GitHub Apps**](https://github.com/settings/applications).
2.  Find **Streamlit** and click **Configure**.
3.  Scroll down to **Organization access**.
4.  Find the organization (e.g., `Brothertown-Language`) and click **Grant** (or **Request** if you are not an owner).
5.  Once granted, the repository will appear in the "Create app" list on Streamlit Cloud.

### Deployment Settings
- **Main file path**: `src/frontend/app.py`
- **App URL**: `https://snea-edit.streamlit.app`

## 2. Supabase (Database)

The database is hosted on **Supabase (PostgreSQL)**.

## 3. GitHub OAuth (Authentication)

Authentication is handled via **GitHub OAuth** integrated into the Streamlit application.
