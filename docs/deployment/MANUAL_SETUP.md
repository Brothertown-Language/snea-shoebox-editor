<!-- Copyright (c) 2026 Brothertown Language -->
# Cloudflare Manual Setup Guide (Permanent)

This guide provides the one-time manual steps required to connect this repository to Cloudflare. Once set up, Cloudflare will automatically pull and deploy your changes from GitHub. No local installation of Node.js/NPM is required.

## 1. BACKEND SETUP (Cloudflare Workers + D1)

### A. Create and Connect the Worker
1.  Navigate to **Workers & Pages** -> **Overview** -> **Create** -> **Worker**.
2.  **Name**: `snea-editor`.
3.  Click **Deploy** (this creates a dummy worker that we will link to GitHub).
4.  Go to the **Settings** tab of the new `snea-editor` worker.
5.  Click **Build** (or **Source Control**) and click **Connect to Git**.
6.  Select the `snea-shoebox-editor` repository.
7.  **Build Settings**:
    - **Production Branch**: `main`
    - **Build Command**: (Leave EMPTY)
    - **Root Directory**: (Leave EMPTY)
8.  Click **Save and Deploy**. Cloudflare will now pull the code and `wrangler.toml` from GitHub.

### B. Bindings and Secrets
1.  Go to **Settings** -> **Variables**.
2.  **D1 Database Bindings**: Click **Add Binding**.
    - **Variable Name**: `DB`
    - **D1 Database**: Select `snea-shoebox` (created by the bootstrap script).
3.  **Secrets**: Click **Add Secret** for each of these:
    - `JWT_SECRET`: (Any long random string)
    - `SNEA_GITHUB_CLIENT_ID`: (From your GitHub OAuth App)
    - `SNEA_GITHUB_CLIENT_SECRET`: (From your GitHub OAuth App)

---

## 2. FRONTEND SETUP (Cloudflare Pages)

1.  Navigate to **Workers & Pages** -> **Overview** -> **Create** -> **Pages** -> **Connect to Git**.
2.  Select the `snea-shoebox-editor` repository.
3.  **Project Name**: `snea-frontend` (or similar).
4.  **Build Settings**:
    - **Framework Preset**: `None`
    - **Build Command**: (Leave EMPTY)
    - **Build output directory**: `/`
5.  **Environment Variables**: Go to **Settings** -> **Variables** and add:
    - `BACKEND_URL`: `https://snea-backend.brothertownlanguage.org`

---

## 3. CUSTOM DOMAINS

1.  **Backend**: Worker -> **Triggers** -> **Custom Domains** -> Add `snea-backend.brothertownlanguage.org`.
2.  **Frontend**: Pages -> **Custom domains** -> Add `snea-editor.brothertownlanguage.org`.
