% SPDX-License-Identifier: MIT

# Runbook — Streamlit Cloud Secrets Outage Remediation (Issue #1397)

**Audience:** developer only. The AI agent cannot reach the Streamlit Cloud
secrets store; this action is performed by a human with Cloud dashboard access.

## Situation

The `snea-edit.streamlit.app` deployment crashes on every page load with:

```
RuntimeError: Missing required secret contact.maintainer_label is not set.
```

Root cause: the deployed Streamlit Cloud secrets store is missing a key that
the app's required-secrets manifest declares. Local dev passed because the
local `.streamlit/secrets.toml` has the key; Cloud does not.

## Remediation — add the missing key in Streamlit Cloud

1. Open the Streamlit Cloud dashboard and select the deployed app
   (`snea-edit.streamlit.app`).
2. Open **Manage app → Settings → Secrets** (the Cloud secrets store editor).
3. Add the missing key PATH under the existing `[contact]` section:

   - `contact.maintainer_label`

   **Name key PATHS only.** Do not paste secret VALUES into the runbook, chat,
   or any tracked file — the Cloud editor is the only place a value is entered.
   The existing local `.streamlit/secrets.toml` shows the expected shape; copy
   the value from there directly into the Cloud editor, never through any
   intermediate file, log, or issue.
4. Save. Streamlit Cloud reboots the app automatically.
5. Confirm the app loads without the RuntimeError.

## Post-remediation confirmation — preflight verification

After fixing the Cloud store, confirm no drift remains by running the
preflight verification from issue #1397 (SC-2):

```bash
uv run python -c "
import tomllib, pathlib
from src.services.secrets_preflight import (
    check_required_secrets, load_required_secret_paths,
)
store = tomllib.loads(pathlib.Path('.streamlit/secrets.toml').read_text())
report = check_required_secrets(store, load_required_secret_paths())
print(report)
"
```

- `{'missing': []}` → the store satisfies every manifest key path.
- Any listed paths are missing keys — add each named PATH to the Cloud store
  exactly as above.

The preflight compares key presence only and never reads, returns, or logs
secret values (SC-5). In production the same preflight runs at startup before
the guard, so future drift surfaces as a structured missing-path report (or a
non-blocking fallback for contact display keys, SC-6) instead of a crash.

## Prevent recurrence

Every future required-secret addition MUST be mirrored into
`.streamlit/required_secrets.yaml` in the same change (the manifest is the
single source of truth consumed by both the preflight and the startup guard).
The preflight reports missing key PATHS to operators before startup fallback
resolution; it never crashes on a missing contact display key.

*Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)*
