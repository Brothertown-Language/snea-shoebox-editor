<!-- Copyright (c) 2026 Brothertown Language -->
# Manual Deployment Guide

This guide provides step-by-step instructions for manually setting up the SNEA Online Shoebox Editor on Cloudflare. We are using one Git repository to serve two distinct subdomains.

## Architecture
- **Frontend**: `snea-editor.brothertownlanguage.org` (Cloudflare Pages)
- **Backend**: `snea-backend.brothertownlanguage.org` (Cloudflare Workers)

---

## 1. Cloudflare Pages (Frontend) Setup

1.  **Log in** to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2.  Navigate to **Workers & Pages** -> **Overview** -> **Create** -> **Pages** -> **Connect to Git**.
3.  Select the `snea-shoebox-editor` repository and click **Begin setup**.
4.  **Configure Build Settings** (This is the section right below "Project Details"):
    *   **Project Name**: `snea-editor`
    *   **Production Branch**: `main`
    *   **Framework Preset**: Select **None** (found in the "Build settings" section).
    *   **Build Command**: Leave this **Empty**.
    *   **Build output directory**: `/`
5.  **Environment Variables**:
    - Navigate to **Settings** -> **Environment variables** for the project.
    - Add `BACKEND_URL`: `https://snea-backend.brothertownlanguage.org`
6.  **Custom Domain**:
    - Navigate to **Custom domains** -> **Set up a custom domain**.
    - Enter `snea-editor.brothertownlanguage.org`.
    - Follow the prompts to update DNS (Cloudflare usually handles this automatically if your domain is managed there).

### Post-Setup: Updating Build Settings
If you have already created the Pages project and need to change these settings:
1.  Navigate to **Workers & Pages** -> **Overview** -> `snea-editor`.
2.  Go to the **Settings** tab.
3.  Click **Builds & deployments** (this is usually a link in the horizontal sub-menu under the "Settings" tab, or a section on the main Settings page).
4.  Look for the **Build settings** section and click **Edit configurations**.
5.  Update the **Build command** (Empty) and **Build output directory** (`/`).
6.  Click **Save**.
6.  *Note*: You may need to trigger a new deployment (via the **Deployments** tab) for the changes to take effect.

---

## 2. Cloudflare D1 (Database) Setup

1.  Navigate to **Workers & Pages** -> **D1**.
2.  Click **Create database** -> **Dashboard**.
3.  **Database Name**: `snea-shoebox`.
4.  Copy the **Database ID** (UUID).
5.  **Initialize Schema**:
    - Click on the database -> **Console**.
    - You will need to run the SQL initialization script (found in the backend logs or source).

---

## 3. Cloudflare Worker (Backend) Setup

We recommend using the `wrangler` CLI for the first deployment to ensure bindings are correct.

1.  **Update `wrangler.toml`**:
    - Ensure `database_id` matches the one you created in Step 2.
    - Verify `main = "src/backend/worker.py"`.
2.  **Deploy via CLI**:
    ```bash
    npx wrangler deploy
    ```
3.  **Custom Domain**:
    - Navigate to **Workers & Pages** -> **Overview** -> `snea-backend`.
    - Go to **Triggers** -> **Custom Domains**.
    - Click **Add Custom Domain** and enter `snea-backend.brothertownlanguage.org`.
4.  **Add Secrets**:
    - Use the dashboard (Settings -> Variables) or CLI to add the following secrets:
      - `JWT_SECRET`: A long random string.
      - `SNEA_GITHUB_CLIENT_ID`: From your GitHub OAuth App.
      - `SNEA_GITHUB_CLIENT_SECRET`: From your GitHub OAuth App.

---

## 4. GitHub OAuth Setup

1.  Go to your GitHub Organization/Account **Settings** -> **Developer settings** -> **OAuth Apps**.
2.  Create a new app (or update the existing one):
    - **Homepage URL**: `https://snea-editor.brothertownlanguage.org`
    - **Authorization callback URL**: `https://snea-backend.brothertownlanguage.org/auth/callback`
3.  Copy the Client ID and Secret to the Worker secrets in Step 3.
