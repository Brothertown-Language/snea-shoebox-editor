<!-- Copyright (c) 2026 Brothertown Language -->
# Cloudflare Manual Setup Guide (Permanent)

This guide provides the one-time manual steps required to connect this repository to Cloudflare. Once set up, Cloudflare will automatically pull and deploy your changes from GitHub. No local installation of Node.js/NPM is required.

> **Note**: Cloudflare is transitioning from separate "Workers" and "Pages" products into a unified "Workers" platform. This guide reflects the modern unified flow.

## 1. BACKEND SETUP (Cloudflare Worker + D1)

### A. Create and Connect the Worker
1.  Navigate to **Workers & Pages** -> **Overview** -> **Create**.
2.  Select **Create application** -> **Import a repository** (or click **Get started** next to **Import a repository**).
3.  Connect your GitHub account if not already connected and select the `snea-shoebox-editor` repository.
4.  **Project Name**: `snea-backend` (or leave the default and it will be updated by GitHub).
5.  **Build Settings**:
    - **Production Branch**: `main`
    - **Build Command**: (Leave EMPTY)
    - **Root Directory**: (Leave EMPTY)
6.  Click **Save and Deploy**. Cloudflare will now pull the code and `wrangler.toml` (which sets the name to `snea-backend`) from GitHub.
7.  *Note: If you already created a Worker manually without Git integration, go to its **Settings** -> **Builds** -> **Connect** to link the repository.*

### B. Bindings and Secrets
1.  Go to **Settings** -> **Variables**.
2.  **D1 Database Bindings**: Click **Add Binding**.
    - **Variable Name**: `DB`
    - **D1 Database**: Select `snea-shoebox` (created by the bootstrap script).
3.  **Secrets**: Click **Add Secret** for each of these:
    - `JWT_SECRET`: (Any long random string)
    - `SNEA_GITHUB_CLIENT_ID`: (Use the value from `PROD_SNEA_GITHUB_CLIENT_ID` in your `.env`)
    - `SNEA_GITHUB_CLIENT_SECRET`: (Use the value from `PROD_SNEA_GITHUB_CLIENT_SECRET` in your `.env`)

---

## 2. FRONTEND SETUP (Cloudflare Workers Assets / Pages)

1.  Navigate to **Workers & Pages** -> **Overview** -> **Create**.
2.  Click **Create application** (if visible) or select the **Pages** tab (Cloudflare is merging these; both currently lead to the same repository connection flow for static assets).
3.  Click **Connect to Git** and select the `snea-shoebox-editor` repository.
4.  **Project Name**: `snea-editor`.
5.  **Build Settings**:
    - **Framework Preset**: `None`
    - **Build Command**: (Leave EMPTY)
    - **Build output directory**: `/`
6.  **Environment Variables**: Go to **Settings** -> **Variables** and add:
    - `BACKEND_URL`: `https://snea-backend.brothertownlanguage.org`

---

## 3. CUSTOM DOMAINS

1.  **Backend**: Worker -> **Triggers** -> **Custom Domains** -> Add `snea-backend.brothertownlanguage.org`.
2.  **Frontend**: Project -> **Custom domains** -> Add `snea-editor.brothertownlanguage.org`.
