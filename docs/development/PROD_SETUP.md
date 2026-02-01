<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Infrastructure & Production Setup Guide

This guide is for **Administrators** and **Infrastructure Leads** who need to bootstrap the Cloudflare and GitHub infrastructure for the SNEA Online Shoebox Editor.

**If you are a Developer just looking to run the app locally, please follow the [Local Setup Guide](SETUP.md) instead.**

## 1. Master Keys Preparation

Before initializing the infrastructure, you must obtain the necessary "Master Keys". These keys are used once by the bootstrap script and then stored securely in GitHub Secrets.

1.  **Generate Cloudflare API Token**:
    Cloudflare uses a scoped token for automated deployments and infrastructure management.

    *   **User API Token setup**:
        *   Go to the [**Cloudflare Dashboard > API Tokens**](https://dash.cloudflare.com/profile/api-tokens).
        *   Click **Create Token** and use the **Get started** button next to **Create Custom Token**.
        *   Create a token with the following permissions:
            *   `Account` | `D1` | `Edit`
            *   `Account` | `Workers Scripts` | `Edit`
            *   `Account` | `Cloudflare Pages` | `Edit`
            *   `Account` | `Account Settings` | `Read` (REQUIRED)
            *   `Zone` | `Workers Routes` | `Edit`
            *   `Zone` | `DNS` | `Read`
        *   **Note**: `Workers KV Storage` and `Workers R2 Storage` are NOT required.
        *   **Verification**: Your token summary should confirm access to "All accounts" for the listed Workers/Pages/D1 permissions and "All zones" for DNS/Workers Routes.

2.  **Generate GitHub Personal Access Token (PAT)**:

    *   Go to [**Settings** > **Developer settings** > **Personal access tokens** > **Fine-grained tokens**](https://github.com/settings/tokens?type=beta).
    *   **Resource owner**: Select **Brothertown-Language** (Crucial: Select the Organization, not your personal account).
    *   **Repository access**: Select **Only select repositories** and pick `Brothertown-Language/snea-shoebox-editor`.
    *   **Permissions**:
        *   `Repository permissions` > `Contents`: **Read and write**.
        *   `Repository permissions` > `Secrets`: **Read and write** (REQUIRED for `bootstrap_env.py`).
        *   `Repository permissions` > `Metadata`: **Read-only**.
    *   **Expiration**: Set to **30 days**.

3.  **Register GitHub OAuth Application**:
    Register the production GitHub OAuth Application for the live site.

    *   **Registration**: [GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**](https://github.com/settings/applications/new).
    *   **Application Name**: `SNEA Shoebox Editor`
    *   **Homepage URL**: `https://snea-editor.michael-conrad.com`
    *   **Application Description**: `Collaborative, version-controlled editing of Southern New England Algonquian (SNEA) linguistic records in MDF format.`
    *   **Authorization callback URL**: `https://snea-editor.michael-conrad.com`
    *   **Enable Device Flow**: **Off** (uncheck)
    *   **Store Credentials**: Save the `Client ID` and `Client Secret` for the next step.

## 2. Infrastructure Bootstrapping (Automated Production Only)

Use the `bootstrap_env.py` script to automate Cloudflare and GitHub infrastructure setup for the **Production** environment.

> **IMPORTANT**: This script is **ONLY** for production infrastructure. Do NOT run this for local development. Local development uses a built-in simulation and does not require Cloudflare tokens.

1.  **Configure Environment Variables**:
    Create or update your `.env` file in the project root with all the keys collected in Section 1 using the `PROD_` prefix. **Important:** Ensure these match the structure in **[SECURITY_ROTATION.md](SECURITY_ROTATION.md)** if you are rotating keys.

    ```env
    # GitHub OAuth (Production Credentials)
    PROD_SNEA_GITHUB_CLIENT_ID="your_production_client_id"
    PROD_SNEA_GITHUB_CLIENT_SECRET="your_production_client_secret"

    # Production Bootstrap (Administrators Only)
    PROD_CF_EMAIL="your_cloudflare_email"
    PROD_CF_API_KEY="your_cloudflare_global_api_key"
    PROD_CF_API_TOKEN="your_cloudflare_user_token"
    PROD_GH_TOKEN="your_github_pat"
    ```

    *Note: We use the `PROD_` prefix to avoid any conflict with your local development environment variables.*

2.  **Run Bootstrap Script**:
    You must run this locally (requires Python and `uv` installed).

    ```bash
    # Install dependencies and run
    uv venv && source .venv/bin/activate
    uv pip install -e .
    uv run python bootstrap_env.py
    ```

    *Note: If custom domains do not appear in your Cloudflare dashboard after running `bootstrap_env.py`, you must run the specialized domain initialization script. **Note: This requires the Worker and Pages project to be deployed first (see Section 3).***

    ```bash
    uv run python bootstrap_domains.py
    ```

    **What `bootstrap_env.py` does automatically**:
    *   Creates the `snea-shoebox` D1 database on Cloudflare.
    *   Generates a secure `JWT_SECRET`.
    *   Uploads all secrets to your GitHub Repo Secrets for CI/CD.
        *   **Note on Secret Names**: GitHub forbids repository secrets starting with `GITHUB_`. Consequently, OAuth credentials are saved as `SNEA_GITHUB_CLIENT_ID` and `SNEA_GITHUB_CLIENT_SECRET`. The backend code is configured to use these prefixed variables in production to ensure they don't overlap with local development settings.
    *   Generates a `wrangler.toml` file.

    **What `bootstrap_domains.py` does**:
    *   Configures Custom Domains for Cloudflare Pages and Workers via REST API.

3.  **Manual Finalization / Automated Domain Setup**

After running the bootstrap script, the infrastructure is ready, but the code needs to be deployed before custom domains can be finalized.

1.  **Trigger Initial Deployment**:
    *   The bootstrap script created the infrastructure, but the code needs to be deployed via GitHub Actions.
    *   Go to your GitHub repository > **Actions**.
    *   Select the **Deploy** workflow (usually `Deploy to Cloudflare`).
    *   Click **Run workflow** (if `workflow_dispatch` is enabled) or push a small change to the `main` branch to trigger it.

2.  **Run Domain Bootstrap (Optional but Recommended)**:
    Once the first deployment is successful, you can run the domain script to automate custom domain linking:
    ```bash
    uv run python bootstrap_domains.py
    ```

3.  **Verify Custom Domains (Manual Check)**:
    If you didn't run the script or want to double-check:
    *   **Cloudflare Pages (Frontend)**:
        1.  Navigate to **Workers & Pages** > **Overview** > `snea-editor`.
        2.  Go to the **Custom domains** tab and ensure `snea-editor.michael-conrad.com` is active.
        3.  *Troubleshooting*: If it says "Not configured", click **Set up a custom domain** and enter `snea-editor.michael-conrad.com`.
    *   **Cloudflare Workers (Backend)**:
        1.  Navigate to **Workers & Pages** > **Overview** > `snea-backend`.
        2.  Go to the **Settings** tab > **Triggers** and ensure `snea-backend.michael-conrad.com` is listed in the **Custom Domains** section.
        3.  *Troubleshooting*: If missing, click **Add Custom Domain** and enter `snea-backend.michael-conrad.com`.

    **Note on Propagation**: It may take a few minutes for the domains to show as "Active" (Green) while Cloudflare issues SSL certificates.

4.  **Database Migration (First Run Only)**:
    *   If your deployment workflow doesn't automatically run migrations, you may need to seed the database:
        ```bash
        npx wrangler d1 execute snea-shoebox --remote --file=./src/backend/schema.sql
        ```

5.  **Verification**:
    *   Visit `https://snea-editor.michael-conrad.com`.
    *   Attempt to log in via GitHub.
    *   Verify that you can see the initial record set (e.g., Natick records).

### Appendix: Production Environment Variables

In the Cloudflare Workers environment (Production), the following variables are injected via GitHub Actions:

| Secret Name | Worker Environment Variable | Description |
|-------------|----------------------------|-------------|
| `CLOUDFLARE_API_TOKEN` | *Used by CI/CD only* | Token for deployment. |
| `CLOUDFLARE_ACCOUNT_ID` | `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Account ID. |
| `JWT_SECRET` | `JWT_SECRET` | Secret for signing session tokens. |
| `SNEA_GITHUB_CLIENT_ID` | `SNEA_GITHUB_CLIENT_ID` | Production GitHub OAuth Client ID (prefixed to avoid GitHub's restricted naming). |
| `SNEA_GITHUB_CLIENT_SECRET` | `SNEA_GITHUB_CLIENT_SECRET` | Production GitHub OAuth Client Secret. |

The backend code prefers `SNEA_*` variables in production and falls back to non-prefixed names in local/dev.

#### Set Worker Secrets via Wrangler

Run these commands from the project root to set secrets in the Cloudflare Worker:

```bash
npx wrangler secret put JWT_SECRET
npx wrangler secret put SNEA_GITHUB_CLIENT_ID
npx wrangler secret put SNEA_GITHUB_CLIENT_SECRET
```

If your frontend origin is fixed and you want to enforce it on the Worker side too, set:

```bash
npx wrangler secret put SNEA_FRONTEND_URL
```

#### Configure Pages Project Variables

In Cloudflare Pages project settings:
- Add `BACKEND_URL` pointing to your Worker URL (e.g., `https://snea-backend.michael-conrad.com`).
- Optionally mirror `SNEA_FRONTEND_URL` for documentation and CI usage (Pages URL).

These are not required by the Worker, but your frontend code (or example) may read `BACKEND_URL` to know where to call the API.
