<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Cloudflare Pages OAuth (GitHub) — Minimal Example

This example shows a minimal static frontend flow (vanilla JS) for Cloudflare Pages that works with the Worker OAuth endpoints:

- `GET /api/auth/github` → returns `{ url, redirect_uri }`
- `POST /api/auth/callback` with `{ code }` → returns `{ user, token }`

Set `SNEA_FRONTEND_URL` (Pages URL) and `SNEA_GITHUB_CLIENT_ID`/`SNEA_GITHUB_CLIENT_SECRET` on the Worker. On Pages, configure an environment variable `BACKEND_URL` pointing to your Worker URL if needed.

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>SNEA Login (GitHub)</title>
  </head>
  <body>
    <button id="login">Login with GitHub</button>
    <pre id="out"></pre>
    <script>
      const BACKEND = window.BACKEND_URL || "https://<your-worker-subdomain>.workers.dev";

      async function startLogin() {
        const r = await fetch(`${BACKEND}/api/auth/github`);
        const data = await r.json();
        window.location.href = data.url; // Redirect to GitHub
      }

      async function completeLogin(code) {
        const r = await fetch(`${BACKEND}/api/auth/callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code })
        });
        const data = await r.json();
        document.getElementById('out').textContent = JSON.stringify(data, null, 2);
        // Store token in memory or as HttpOnly cookie set by the Worker (recommended)
      }

      // Handle ?code= on return from GitHub
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      if (code) {
        completeLogin(code);
      }

      document.getElementById('login').addEventListener('click', startLogin);
    </script>
  </body>
  </html>
```

Notes:
- Ensure your GitHub OAuth App redirect/callback URL matches the Pages URL you deploy (and your `SNEA_FRONTEND_URL`).
- For production, prefer issuing an HttpOnly, `SameSite=Lax` cookie from the Worker after `/api/auth/callback` and avoid exposing raw bearer tokens to JS when possible.
