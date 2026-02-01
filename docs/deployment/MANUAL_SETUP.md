<!-- Copyright (c) 2026 Brothertown Language -->
# Cloudflare Manual Setup Guide (Permanent)

This guide provides the one-time manual steps required to connect this repository to Cloudflare. Once set up, Cloudflare will automatically pull and deploy your changes from GitHub. No local installation of Node.js/NPM is required.

> **Note**: Cloudflare is transitioning from separate "Workers" and "Pages" products into a unified "Workers" platform. This guide reflects the modern unified flow.

## 1. PREREQUISITES: The Cloudflare API Token

Before starting the setup, you must have a Cloudflare API Token. This token is what allows GitHub to talk to Cloudflare.

**Tip**: If you have existing tokens and are unsure which is which, **delete them both** and create one fresh token following the steps below. This ensures you start with the correct permissions.

1.  **Create the Token**:
    -   Go to the [Cloudflare Dashboard > My Profile > API Tokens](https://dash.cloudflare.com/profile/api-tokens).
    -   Click **Create Token**.
    -   Find **Create Custom Token** (at the top) and click **Get started**.
2.  **Set Permissions**: Name the token `snea-deploy-token` and add these **3 specific permissions**:
    -   `Account` | `Cloudflare Pages` | `Edit`
    -   `Account` | `Workers Scripts` | `Edit`
    -   `Account` | `D1` | `Edit`
3.  **Save the Token**:
    -   Click **Continue to summary** -> **Create Token**.
    -   **COPY THE TOKEN IMMEDIATELY.** It will never be shown again.
    -   Paste this token into your `.env` file as `PROD_CF_API_TOKEN`.
    -   *(If you run `bootstrap_env.py`, it will automatically upload this token to GitHub as a secret named `CLOUDFLARE_API_TOKEN`.)*

---

## 2. BACKEND SETUP (Cloudflare Worker + D1)

### A. Create and Connect the Worker
1.  Navigate to **Workers & Pages** -> **Overview** -> **Create**.
2.  Select **Create application** -> **Import a repository** (or click **Get started** next to **Import a repository**).
3.  Connect your GitHub account if not already connected and select the `snea-shoebox-editor` repository.
    - *Tip: The repository list is a scrollable box that may not show a scrollbar until you scroll it; if you don't see the repo, try scrolling the box.*
4.  **Project Name**: `snea-backend` (or leave the default and it will be updated by GitHub).
5.  **Set up your application**:
    - **Build command**: `uv pip install -e . && uv sync --all-groups`
    - **Deploy command**: `npx wrangler deploy`
    - **Non-production branch deploy command**: `npx wrangler versions upload`
    - **Path**: `/`
    - **Build Settings** (Advanced): Select your API token in the **API Token** dropdown. If it does not appear, click **Add a token** to link it.
        - *Note: Creating a token via the "Add a token" button in this UI may automatically set the required permissions without asking for them (e.g., `snea-backend-build`). This is an acceptable alternative to creating one manually.*
6.  **Build Settings**:
    - **Production Branch**: `main`
    - **Build Command**: `uv pip install -e . && uv sync --all-groups`
    - **Root Directory**: (Leave EMPTY)
7.  Click **Save and Deploy**. Cloudflare will now pull the code and `wrangler.toml` (which sets the name to `snea-backend`) from GitHub.
8.  *Note: If you already created a Worker manually without Git integration, go to its **Settings** -> **Builds** -> **Connect** to link the repository.*

### B. Bindings and Secrets (Automated)

If you have already run `python3 bootstrap_env.py` (which uses the token from Step 1), the following are handled for you:
-   **API Token**: `CLOUDFLARE_API_TOKEN` is uploaded to GitHub Secrets.
-   **Secrets**: `JWT_SECRET`, `SNEA_GITHUB_CLIENT_ID`, and `SNEA_GITHUB_CLIENT_SECRET` are uploaded to GitHub Secrets.
-   **Wrangler Config**: `wrangler.toml` is generated with your `database_id`.

Next, perform this manual step in the Cloudflare Dashboard for the `snea-backend` worker:

1.  **D1 Database Binding**:
    -   Go to the `snea-backend` Worker -> **Settings** -> **Variables**.
    -   Click **Add Binding**.
    -   **Variable Name**: `DB`
    -   **D1 Database**: Select `snea-shoebox`.
    -   Click **Save and Deploy**.

---

## 3. FRONTEND SETUP (Cloudflare Workers Assets / Pages)

1.  Navigate to **Workers & Pages** -> **Overview** -> **Create**.
2.  Select **Create application** -> **Import a repository** (or click **Get started** next to **Import a repository**).
3.  Connect your GitHub account and select the `snea-shoebox-editor` repository.
    - *Tip: The repository list is a scrollable box that may not show a scrollbar until you scroll it; if you don't see the repo, try scrolling the box.*
4.  **Project Name**: `snea-editor`.
5.  **Set up your application**:
    - **Build command**: `uv pip install -e . && uv sync --all-groups`
    - **Deploy command**: `npx wrangler pages deploy . --config wrangler.pages.toml`
    - **Non-production branch deploy command**: `npx wrangler pages deploy . --config wrangler.pages.toml`
    - **Path**: `/`
    - **Build Settings** (Advanced): Select your API token in the **API Token** dropdown. If it does not appear, click **Add a token** to link it.
        - *Note: Creating a token via the "Add a token" button in this UI may automatically set the required permissions without asking for them (e.g., `snea-frontend-build`). This is an acceptable alternative to creating one manually.*
6.  **Build Settings**:
    - **Production Branch**: `main`
    - **Framework Preset**: `None`
    - **Build Command**: `uv pip install -e . && uv sync --all-groups`
    - **Build output directory**: `.` (The current directory)
7.  Click **Save and Deploy**. Cloudflare will now treat this as a Workers Assets (Pages) project.
8.  **Environment Variables**: After deployment, go to the project's **Settings** -> **Variables** and add:
    - `BACKEND_URL`: `https://snea-backend.brothertownlanguage.org`

---

## 4. CUSTOM DOMAINS
1.  **Backend**: Worker -> **Settings** -> **Domains & Routes** -> **Add Custom Domain** -> Add `snea-backend.brothertownlanguage.org`.
2.  **Frontend**: Project -> **Settings** -> **Custom domains** -> **Add Custom Domain** -> Add `snea-editor.brothertownlanguage.org`.
