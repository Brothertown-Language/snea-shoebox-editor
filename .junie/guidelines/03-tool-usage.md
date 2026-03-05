# Tool Usage & Terminal Rules

## Verification

- Never use `sed -i`. Use IDE tools (`multi_edit`, `search_replace`) for all file modifications. Verify file/path claims
  with a tool call (`ls`, `open`, `search_project`).
- If a tool call fails or is inconclusive, state it and retry with a different tool.

## Path Rules (ZERO TOLERANCE)

- **ABSOLUTE PATHS ARE FORBIDDEN IN ALL AGENT TERMINAL COMMANDS.**
  Never pass a path beginning with `/` to any terminal command or tool parameter.
  Violating this rule is a critical error regardless of context, convenience, or tool defaults.
  This applies to hardcoded paths typed by the agent as CLI arguments or tool parameters. It does not prohibit scripts from computing absolute paths at runtime (e.g., via `Path(__file__).resolve()` or `git rev-parse`).
- The terminal is always at project root. Use relative paths from project root for every command:
  ✅ `ls plans/archive/`
  ❌ `ls /home/michael/git/newsrx-genai-python/plans/archive/`
- Never issue a `cd` command. Run all commands from project root using relative paths.
  (Authored scripts/shell headers may use `cd` for root resolution per `09-scripting.md`.)
- If you find yourself about to type a `/`-prefixed path, STOP — rewrite it as a relative path first.

## Command Restrictions

- No `stty` (hangs non-interactive sessions).
- No destructive checkouts (`git checkout` files / discard uncommitted changes).
- No embedded scripts via heredocs — use standalone script files.
- No multi-statement shell one-liners or inline script blobs (`python -c`, `ruby -e`). If a command exceeds a single
  simple statement, create a script in `tmp/` and execute it.
- **One clear command per invocation.** Each terminal call must be a single, human-parseable command. A short `&&`
  guard (e.g., `mkdir -p tmp && uv run python tmp/script.py`) is acceptable when the second command depends on the
  first. No subshells, pipes-of-pipes, process substitution, or multi-stage chains. If the task requires more, create a
  script in `tmp/` and run it.
- **`grep` IS UNRELIABLE in this environment.** It hangs, produces broken pipes, and silently fails in non-interactive
  terminal sessions. Do NOT use `grep`, `egrep`, or `zgrep` — not even as a last resort, not even piped.
  Use designated search tools (`search_project`, `ai_bin/src-search`, `ai_bin/guidelines-search`) exclusively.
  If none cover the need, write a Python script in `tmp/` and run it with `uv run python tmp/script.py`.

## Jupyter Notebook Editing

- **NEVER edit `.ipynb` files via raw JSON manipulation** (direct file writes, `json.dump`, `sed`, string replacement
  on the raw file). This is unreliable and risks notebook corruption.
- **NEVER read `.ipynb` files by parsing raw JSON** (e.g., `python -c "import json; json.load(...)"` or any inline
  script). Use the Jupyter Server REST API or `nbformat` to read notebook content.
- **NEVER use the `open` IDE tool on `.ipynb` files.** The IDE tool does not render notebooks correctly and produces
  unreliable output. Always use Option A (Jupyter Server REST API) or Option B (`nbformat`) below.
- Always create new or update existing `ai_bin/` scripts for notebook editing tasks. The scripts should be
  self-contained, well-documented, and follow the agent's coding style. The implementations should switch between Option A and Option B automatically.

### Option A: Jupyter Server REST API (preferred)

**Option A is the default for all notebook editing tasks.** At the start of any notebook task,
start a Jupyter server on port 18888 (if not already running). This server runs independently
of PyCharm — PyCharm connects its own kernel when the notebook is opened in the IDE and is
not affected by the agent's server on 18888.

**Start a server (background, port 18888):**
```bash
uv run python ai_bin/jupyter-start
```

**Key endpoints:**
- `GET  /api/contents/<path>` — fetch notebook as structured JSON
- `PUT  /api/contents/<path>` — update notebook (server validates structure before saving)
- `POST /api/sessions`        — create a kernel session
- `POST /api/kernels/<id>/execute` — execute code in a running kernel
- `PATCH /api/contents/<path>` — partial update (Jupyter Server ≥ 2.x)

**Workflow (Python / `requests`):**
```python
import requests

BASE = "http://localhost:18888"
r = requests.get(f"{BASE}/api/contents/pubmed_data_3/0200_scan_seed_candidates.ipynb")
nb = r.json()
# mutate nb["content"]["cells"] as needed — cell source is plain Python strings
requests.put(f"{BASE}/api/contents/pubmed_data_3/0200_scan_seed_candidates.ipynb",
             json={"type": "notebook", "content": nb["content"]})
```

- The server validates notebook structure before saving; execution counts and output metadata
  are managed automatically.
- Cell `source` fields are plain Python strings — the agent never needs to touch raw JSON,
  metadata, or MIME bundles.

### Option B: `nbformat` (fallback only)

Use only if the Jupyter server cannot be started.

- Load with `nbformat.read(f, as_version=4)`
- Manipulate cells using Python objects (`nbformat.v4.new_code_cell()`, etc.)
- Write back with `nbformat.write(nb, f)`
- Place notebook-editing scripts in `tmp/` and execute with `uv run python tmp/script.py`.

## Python Source File Analysis

- When analyzing Python source files to extract classes, methods, functions, or line numbers, always use the built-in `ai_gen/` programs. Add additional programs to `ai_gen/` as needed. The programs should use the
  structural introspection modules (`pyclbr`, `ast`, or `symtable`). Do not grep, search, iterate through the
  filesystem, or request repeated user approvals. Produce results directly from these modules' parsed representations,
  and return only the structured output required for the task.
- Do not assume memory of a file's structure is current. Always reinspect using these modules to ensure you are using
  current information.

## Jupyter Notebook Outputs
- To inspect notebook cell outputs (stdout, stderr, errors, display), always use `uv run python ai_bin/nb-outputs <notebook.ipynb>`.
- Never parse raw notebook JSON to read outputs — use `nb-outputs` exclusively.


## .junie/ File Access

Never use direct read or write methods (`open` tool, `bash cat`/`grep`/`sed`, `search_project`, or any other
ad-hoc file-reading/writing mechanism) on any `.junie/` file. Invoking the designated `ai_bin/` utilities via `bash`
is permitted and required. Always use the designated `ai_bin/` utility:

- `guidelines/` and `guidelines.md` → `uv run python ai_bin/guidelines`
  - To read a subset: `uv run python ai_bin/guidelines --files 02-scope-autonomy.md 03-tool-usage.md`
  - Never use `for`/`cat` shell loops to iterate over guideline files.
- `memory.md` → `uv run python ai_bin/memory`
- `VIOLATION_LOG.jsonl` → `uv run python ai_bin/violation-log`

## `ai_bin/` Agent Tools

- Agent-authored reusable CLI helpers live in `ai_bin/` (project root). This directory is version-controlled and
  exempt from the approval gate — scripts may be created or updated without a prior GO.
- At the start of any session, run `uv run python ai_bin/help` to enumerate all available tools and their descriptions.
- New helpers must follow `09-scripting.md` header conventions and expose a `--help` flag with a `DESCRIPTION:` line
  in their module docstring.
- Invoke tools with `uv run python ai_bin/<tool-name>`.

- **Production Schema Protection**: Scripts authored or executed by the agent that interact with the database MUST check
  the `MARKER_JUNIE_TERMINAL` env var at startup. The variable is considered set if it is present in the environment
  with any non-empty value (i.e., `os.environ.get('MARKER_JUNIE_TERMINAL')`). If set, the script MUST operate only
  against the test schema — never the production schema. If the script cannot guarantee schema isolation, it must abort
  with a clear error message.
