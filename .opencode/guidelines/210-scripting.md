# Scripting Standards

## Script Headers (mandatory)

Every script/notebook MUST include root resolution:

- **Shell**: `cd "$(dirname "$0")" && cd "$(git rev-parse --show-cdup)" || exit 1`
- **Python**:
  `BASE_DIR = Path(__file__).resolve().parent; CDUP = subprocess.check_output(["git", "-C", str(BASE_DIR), "rev-parse", "--show-cdup"], text=True).strip(); PROJECT_ROOT = (BASE_DIR / CDUP).resolve()`
- **Notebooks**: Set `base_dir` using Jupyter's directory hint:
  `base_dir = Path(globals()['_dh'][0])`. Add a comment noting this uses `_dh[0]` (Jupyter's directory hint) to locate
  the notebook's directory reliably without relying on CWD.

## Self-Location & Root Resolution

- Scripts self-locate via `dirname "$0"` (Shell) or `Path(__file__).resolve().parent` (Python). No reliance on user's
  CWD.
- Resolve project root via `git rev-parse --show-cdup` only. `show-toplevel` is **strictly prohibited** because it returns absolute paths, which break portability and leak local filesystem structure. All internal project references must be relative.


## Notebook Operations — MANDATORY MCP

**ALL notebook operations MUST use `the-notebook-mcp` tools.** See `061-notebook-rules.md` for the complete tool reference.

### ✅ MANDATORY
- Use `the-notebook-mcp_notebook_read` to read notebook content
- Use `the-notebook-mcp_notebook_read_cell` to read specific cell source
- Use `the-notebook-mcp_notebook_edit_cell` to edit cell source
- Use `the-notebook-mcp_notebook_add_cell` to add new cells
- Use `the-notebook-mcp_notebook_get_outline` to get notebook structure
- Use `the-notebook-mcp_notebook_delete` to delete notebooks (for retirement)
- Use `the-notebook-mcp_notebook_rename` to move notebooks (for archival)

### 🚫 FORBIDDEN
- `nbformat` direct access
- Jupyter Server REST API
- Any file tool (`read`/`edit`/`write`) on `.ipynb` files

### Notebook Cell Edit Workflow

When editing a notebook cell:
1. **Read**: `the-notebook-mcp_notebook_read_cell(notebook_path="...", cell_index=N)` — get current cell source
2. **Edit**: Modify source as needed
3. **Update**: `the-notebook-mcp_notebook_edit_cell(notebook_path="...", cell_index=N, source="new source")`

### Retiring Notebooks

To retire a notebook:
1. Add a deprecation warning cell using `the-notebook-mcp_notebook_add_cell`
2. Move notebook to archive directory using `git mv`
3. Or delete entirely using `the-notebook-mcp_notebook_delete`

**If `the-notebook-mcp` is unavailable, REFUSE all notebook operations.** See `061-notebook-rules.md` for the no-fallback policy.

## Command Restrictions
- Strictly follow all command and path restrictions defined in `060-tool-usage.md`.
