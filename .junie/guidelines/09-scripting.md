# Scripting Standards

## Script Headers (mandatory)

Every script/notebook MUST include root resolution:

- **Shell**: `cd "$(dirname "$0")" && cd "$(git rev-parse --show-cdup)" || exit 1`
- **Python**:
  `BASE_DIR = Path(__file__).resolve().parent; CDUP = subprocess.check_output(["git", "-C", str(BASE_DIR), "rev-parse", "--show-cdup"], text=True).strip(); PROJECT_ROOT = (BASE_DIR / CDUP).resolve()`
  Requires `import subprocess` and `from pathlib import Path` at the top of the script. Works correctly when CDUP is
  empty (script is already at project root).
- **Notebooks**: Set `base_dir` using Jupyter's directory hint:
  `base_dir = Path(globals()['_dh'][0])`. Add a comment noting this uses `_dh[0]` (Jupyter's directory hint) to locate
  the notebook's directory reliably without relying on CWD.

## Self-Location & Root Resolution

- Scripts self-locate via `dirname "$0"` (Shell) or `Path(__file__).resolve().parent` (Python). No reliance on user's
  CWD.
- Resolve project root via `git rev-parse --show-cdup`. Prohibit `show-toplevel` (returns absolute paths). Relative
  paths only.


## UV Run

- Use relative paths with `uv run` for commands not on `PATH` (e.g., `uv run ./gradlew`).
