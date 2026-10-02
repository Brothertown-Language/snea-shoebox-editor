> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1397/

## Problem

The `snea-edit.streamlit.app` production deployment is DOWN. Every page load crashes with:

```
RuntimeError: Missing required secret contact.maintainer_label is not set.
Add contact.maintainer_label to .streamlit/secrets.toml (or the deployed secrets store) before starting the app.
```

Source: `streamlit_app.py:232` fail-fast guard introduced by commit `2d37a52` (issue #1392).

BLUF: The guard works as spec'd, but the deploy pipeline never verified the deployed secrets store was updated. Dev passed because local `.streamlit/secrets.toml` contains the key; production crashed because Streamlit Cloud's separate secrets store does not. Tests, local runs, and merge checks all passed against dev secrets — the environment drift was invisible to every verification gate that ran.

## Evidence

- Production log (2026-10-02 02:56 UTC): repeated identical tracebacks, `KeyError: 'maintainer_label'` → `RuntimeError` at `streamlit_app.py:234`. Saved at `tmp/logs-brothertown-language-snea-shoebox-editor-main-streamlit_app.py-2026-10-02T02_58_12.295Z.txt`.
- Commit `2d37a52` (feat(app): fail-fast startup validation for contact.maintainer_label, Refs #1392) merged to `main`.
- Issue #1392 spec Scope required only: "Document the required contact key in the `.streamlit/` secrets templates and local-development docs so deployed environments can supply it" — documentation, not deployment verification.

## Root Cause (process gap, not just the missing key)

The fix is NOT merely "add the secret" — that is the symptom remediation. The root cause is that no pipeline gate verifies that a required-secret addition is mirrored to each deployed environment before/at deploy time. Any future change adding a required secret will reproduce this outage. Required-secrets drift between local dev and deployed stores is currently undetectable until production crashes.

## Scope

- Define a machine-checkable inventory of required secrets keys (e.g. a manifest listing required `st.secrets` paths such as `contact.maintainer_label`, `contact.mastodon_url`)
- Add a verification mechanism that checks a deploy target's secrets store against the required-secrets inventory BEFORE the app can crash in production (e.g. a startup preflight that emits a structured report, or a CI/deploy step; exact mechanism to be determined in spec)
- Remediate the current production outage: supply `contact.maintainer_label` in the Streamlit Cloud secrets store (human/developer action — agent cannot reach the Cloud store)
- Never log or expose secret VALUES — inventory checks compare key presence only

**Out of scope:**

- Removing or weakening the fail-fast guard (it performed correctly)
- Redesigning the contact dialog or resolution path
- Restructuring the secrets file format

## Approach

Introduce a required-secrets manifest as the single machine-readable source of truth for every `st.secrets` key the app requires. Build a preflight check (startup-time or CI/deploy-time, mechanism to be finalized in spec) that compares the deploy target's secrets store against the manifest and fails with a structured, actionable report naming only missing key PATHS — never values. Mirror any required-secret addition into the manifest as part of the same change that adds it, so drift between environments is caught before deploy rather than by a production crash.

## Impact

- **Risk: secrets exposure** — verification must compare key presence only; mitigate by asserting no value logging in the preflight implementation and tests.
- **Risk: manifest drift** — a stale manifest could mask future missing keys; mitigate by tying the preflight to the fail-fast guard's key list so the two cannot diverge silently.
- **Key dependency:** immediate outage remediation requires the developer to add `contact.maintainer_label` in the Streamlit Cloud secrets store (agent cannot reach the Cloud store).
- **Call to action:** developer action required now to restore production; spec work proceeds in parallel to close the process gap.

🤖 OpenCode (huggingface/zai-org/GLM-5.3-Flash) created
