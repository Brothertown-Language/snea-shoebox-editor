<!-- Copyright (c) 2026 Brothertown Language -->
# Cloudflare Manual Setup Guide (Permanent)

This guide provides the one-time manual steps required to connect this repository to Cloudflare. Once set up, Cloudflare will automatically pull and deploy your changes from GitHub. No local installation of Node.js/NPM is required.

## 1. BACKEND SETUP (Cloudflare Workers + D1)

### A. Create and Connect the Worker
1.  Navigate to **Workers & Pages** -> **Overview** -> **Create** -> **Worker**.
2.  Change the name to **`snea-backend`** (or leave the default and it will be updated by GitHub) and click **Deploy**.
3.  On the "Success" page, click **Edit Code** or **Go to Dashboard**.
4.  Navigate to the **Settings** tab of your new worker.
5.  Click **Build** (or **Source Control**) in the sidebar and click **Connect to Git**.
6.  Select the `snea-shoebox-editor` repository.
7.  **Build Settings**:
    - **Production Branch**: `main`
    - **Build Command**: (Leave EMPTY)
    - **Root Directory**: (Leave EMPTY)
8.  Click **Save and Deploy**. Cloudflare will now pull the code and `wrangler.toml` (which sets the name to `snea-backend`) from GitHub.

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

## 2. FRONTEND SETUP (Cloudflare Pages)

1.  Navigate to **Workers & Pages** -> **Overview** -> **Create** -> **Pages** -> **Connect to Git**.
2.  Select the `snea-shoebox-editor` repository.
3.  **Project Name**: `snea-editor`.
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
