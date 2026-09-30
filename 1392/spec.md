---
remote_issue: 1392
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1392
promoted_at: 2026-09-30T17:10:00Z
labels:
  - needs-approval
---

# SPEC-FIX: Unrendered `<MAINTAINER_CONTACT>` Placeholder Leaks Into UI

## Problem

The "Access Restricted" dialog on the login page renders a raw, unrendered `<MAINTAINER_CONTACT>` template placeholder to end users instead of the intended maintainer contact text. The placeholder was never resolved because no substitution mechanism exists in the codebase. Introduced in commit 36c7153 ("Batch implementation: 17 issues"), likely copied from a template whose placeholder-substitution step never landed. Visible at localhost:8501.

## Root Cause (verified during diagnosis)

- Literal string hardcoded in 3 call sites: `src/frontend/pages/login.py:32`, `streamlit_app.py:124`, `streamlit_app.py:201`
- No substitution mechanism anywhere: grep across the repo finds only those 3 hits; no env var, secret key, or build step defines/replaces it
- The Mastodon URL itself renders fine via `st.secrets["contact"]["mastodon_url"]` (`.streamlit/secrets.toml`)

## Approach

Resolve the placeholder through the existing `st.secrets` mechanism, which already successfully supplies `contact.mastodon_url`. The 3 hardcoded call sites will be replaced with a single resolution path sourced from secrets/config (with a clear fail-fast error if the secret is absent), or the text rewritten to avoid the `<...>` template form entirely.

## Impact

- Risk: placeholder resolution fails if secrets.toml lacks the new key → fail-fast error with actionable message at startup
- Risk: multiple call sites drifting again → consolidate to one single source of truth
- Risk: deployed environments missing the secret → document the key in `.streamlit/secrets.toml` example/docs

---
🤖 OpenCode (ollama-cloud/glm-5.3-flash) created
