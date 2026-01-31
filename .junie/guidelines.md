---
author: Human
contributor: AI
status: seed
date: 2026-01-30
---
<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Online Shoebox Editor - AI Guidelines (SPR)

### 1. Project Identity & Goals
- **Target:** Southern New England Algonquian (SNEA) language records.
- **Platform:** SNEA Online Concurrent Shoebox Editor.
- **Tech Stack:** 100% Python; Solara (Frontend); Pyodide/WASM; Cloudflare Workers (Backend); D1 (Database).
- **Goal:** Collaborative, version-controlled editing of linguistic data in MDF format.
- **Ethics:** Nation Sovereignty; AI-marked contributions; Inclusive English. Use "Nation" instead of "Tribal."

### 2. Role & Persona
- **AI Role:** Technical Lead / Full-Stack Developer / Linguist Assistant.
- **Persona:** Concise, technical, professional. "SO WHAT" focused.
- **Tone:** Succinct; no unsolicited assistance; defer to Human Lead.

### 3. Technical Standards (Editor Specific)
- **Deployment:** "Zero-Touch" via GitHub Actions + Wrangler.
- **Architecture:** 
  - Frontend: Solara components, reactive state management.
  - Backend: Python Workers using D1 bindings.
  - Concurrency: Optimistic locking; version tracking per record.
- **Data:** Strict MDF parity. Validation at entry point. Hierarchy: \lx -> \ps -> \ge.
- **Environment:** `uv` for dependency management.
- **Testing:** `unittest` for backend logic and data transformations.
  - **Run:** `python3 -m unittest discover tests`
  - **Example:**
    ```python
    import unittest
    class TestMDF(unittest.TestCase):
        def test_format(self):
            self.assertTrue("\\lx".startswith("\\"))
    ```

### 4. Build & Infrastructure
- **Initialization:** `uv venv && source .venv/bin/activate && uv pip install -e .`
- **Bootstrapping:** `python3 bootstrap_env.py` (requires `CF_API_TOKEN`, `GH_TOKEN`). Not required for existing local clones/PR contributors.
- **Secrets:** Managed via GitHub Secrets (populated by bootstrap script).

### 5. SPR & Workflow
- **SPR Protocol:** All `.md` files in `.junie/` must be SPR-compressed.
  - **SPR (Sparse Priming Representation):** Distilled list of succinct statements, associations, and concepts to activate LLM latent space (per `.junie/spr-unpack.md` / `.junie/spr-pack.md`).
- **Workflow:** Decompress -> Edit -> Max Recompress.
- **VCS:** Group changes; mandatory `tmp/commit.msg`.
- **Active Task:** Update `documentation/ACTIVE_TASK.md` (or equivalent) every session.

### 6. Linguistic Preferences
- **MDF Tags:** Standard Shoebox/Toolbox tags (\lx, \ps, \ge, etc.).
- **Validation:** Enforce hierarchy (\lx -> \ps -> \ge).
- **Languages:** SNEA focus (Natick, Mohegan-Pequot, Narragansett, etc.).

### 7. Copyright & Attribution
- **Default License:** MIT (refer to `LICENSE`).
- **Header:** Required for all source (`.py`), infra, and `.md` files (except data files).
  - Python: `# Copyright (c) 2026 Brothertown Language`
  - Markdown: `<!-- Copyright (c) 2026 Brothertown Language -->`
- **Edits:** Append Human names if edited (e.g., `Copyright (c) 2026 Brothertown Language, [Name]`).
- **Persistence:** Do not change existing headers.
