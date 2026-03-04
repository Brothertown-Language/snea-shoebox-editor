# Tool Usage & Terminal Rules

## Verification

- Never use `sed -i`. Use IDE tools (`multi_edit`, `search_replace`) for all file modifications. Verify file/path claims
  with a tool call (`ls`, `open`, `search_project`).
- If a tool call fails or is inconclusive, state it and retry with a different tool.

## Path Rules (ZERO TOLERANCE)

- **ABSOLUTE PATHS ARE FORBIDDEN IN ALL AGENT TERMINAL COMMANDS.**
  Never pass a path beginning with `/` to any terminal command or tool parameter.
  Violating this rule is a critical error regardless of context, convenience, or tool defaults.
- The terminal is always at project root. Use relative paths from project root for every command:
  ✅ `ls plans/archive/`
  ❌ `ls /home/michael/git/newsrx-genai-python/plans/archive/`
- Never issue a `cd` command. Run all commands from project root using relative paths.
  (Authored scripts/shell headers may use `cd` for root resolution per `09-scripting.md`.)
- If you find yourself about to type a `/`-prefixed path, STOP — rewrite it as a relative path first.

## Python Source File Analysis

- When analyzing Python source files to extract classes, methods, functions, or line numbers, always use the built-in
  structural introspection modules (`pyclbr`, `ast`, `inspect`, or `symtable`). Do not grep, search, iterate through the
  filesystem, or request repeated user approvals. Produce results directly from these modules' parsed representations,
  and return only the structured output required for the task.
- Do not assume memory of a file's structure is current. Always reinspect using these modules to ensure you are using
  current information.

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
- No repeated or iterative `grep`/`zgrep`/`egrep`/`sed` searches. Use designated search tools (`search_project`)
  instead of `grep`/`egrep`/`zgrep` wherever possible. If no search tool covers the need, a single one-off `grep` is
  acceptable as a last resort; if a second search on the same data is needed, consolidate into a Python script in
  `tmp/` instead.
- **Production Schema Protection**: Scripts authored or executed by the agent that interact with the database MUST check
  the `MARKER_JUNIE_TERMINAL` env var at startup. The variable is considered set if it is present in the environment
  with any non-empty value (i.e., `os.environ.get('MARKER_JUNIE_TERMINAL')`). If set, the script MUST operate only
  against the test schema — never the production schema. If the script cannot guarantee schema isolation, it must abort
  with a clear error message.
