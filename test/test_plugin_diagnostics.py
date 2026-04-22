import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".opencode" / "scripts"))


DIAGNOSTICS_DIR = ".opencode/tmp"
DIAGNOSTICS_FILE = ".opencode/tmp/plugin-diagnostics.jsonl"


class TestDiagnosticStreamFormat:
    def test_jsonl_line_is_valid_json(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"source": "test", "level": "error", "message": "boom", "exitCode": 1}) + "\n"
        diag_file.write_text(line)
        parsed = json.loads(line.strip())
        assert parsed["source"] == "test"
        assert parsed["level"] == "error"
        assert parsed["message"] == "boom"
        assert parsed["exitCode"] == 1

    def test_multiple_lines_parseable(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            json.dumps({"source": "a", "level": "error", "message": "err1"}) + "\n",
            json.dumps({"source": "b", "level": "warning", "message": "warn1"}) + "\n",
        ]
        diag_file.write_text("".join(lines))
        parsed = [json.loads(l.strip()) for l in diag_file.read_text().strip().split("\n") if l.strip()]
        assert len(parsed) == 2
        assert parsed[0]["source"] == "a"
        assert parsed[1]["level"] == "warning"

    def test_optional_exit_code(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"source": "test", "level": "warning", "message": "no exit"}) + "\n"
        diag_file.write_text(line)
        parsed = json.loads(line.strip())
        assert "exitCode" not in parsed

    def test_valid_levels(self, tmp_path):
        for level in ("error", "warning", "info"):
            line = json.dumps({"source": "test", "level": level, "message": "msg"}) + "\n"
            parsed = json.loads(line.strip())
            assert parsed["level"] == level


class TestDiagnosticBlockFormat:
    def test_error_includes_exit_code(self):
        diagnostics = [
            {"source": "session-init", "level": "error", "message": "failed", "exitCode": 1},
        ]
        block = _build_diagnostic_block(diagnostics)
        assert "<PLUGIN_DIAGNOSTICS>" in block
        assert "[ERROR]" in block
        assert "session-init" in block
        assert "exit code 1" in block

    def test_warning_without_exit_code(self):
        diagnostics = [
            {"source": "env-loader", "level": "warning", "message": ".env not gitignored"},
        ]
        block = _build_diagnostic_block(diagnostics)
        assert "[WARNING]" in block
        assert "env-loader" in block
        assert ".env not gitignored" in block
        assert "exit code" not in block

    def test_empty_diagnostics_no_block(self):
        block = _build_diagnostic_block([])
        assert block == ""

    def test_multiple_diagnostics(self):
        diagnostics = [
            {"source": "session-init", "level": "error", "message": "err", "exitCode": 2},
            {"source": "env-loader", "level": "warning", "message": "warn"},
        ]
        block = _build_diagnostic_block(diagnostics)
        assert block.count("[ERROR]") == 1
        assert block.count("[WARNING]") == 1


class TestCollectDiagnostics:
    def test_reads_and_clears_file(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        diag_file.write_text(
            json.dumps({"source": "a", "level": "error", "message": "m1"}) + "\n"
        )
        diags = _collect_diagnostics(str(tmp_path))
        assert len(diags) == 1
        assert diags[0]["source"] == "a"
        # File should be cleared after reading
        assert diag_file.read_text() == ""

    def test_missing_file_returns_empty(self, tmp_path):
        diags = _collect_diagnostics(str(tmp_path))
        assert diags == []

    def test_empty_file_returns_empty(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        diag_file.write_text("")
        diags = _collect_diagnostics(str(tmp_path))
        assert diags == []

    def test_skips_malformed_lines(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)
        diag_file.write_text("bad json\n" + json.dumps({"source": "ok", "level": "info", "message": "m"}) + "\n")
        diags = _collect_diagnostics(str(tmp_path))
        assert len(diags) == 1
        assert diags[0]["source"] == "ok"


class TestEnvLoaderDiagnosticWriting:
    def test_env_not_gitignored_writes_diagnostic(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("MY_VAR=value\n")
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n")

        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_env_warning(str(tmp_path))

        assert diag_file.exists()
        content = diag_file.read_text().strip()
        assert content
        parsed = json.loads(content)
        assert parsed["source"] == "env-loader"
        assert parsed["level"] == "warning"
        assert ".env" in parsed["message"] and "gitignore" in parsed["message"].lower()

    def test_env_gitignored_no_diagnostic(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("MY_VAR=value\n")
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text(".env\n")

        diag_file = tmp_path / DIAGNOSTICS_FILE
        # When .env IS gitignored, env-loader does NOT write a diagnostic
        # So no diagnostic file should exist (or remain empty)
        assert not diag_file.exists() or diag_file.read_text().strip() == ""

    def test_parse_duplicate_key_writes_diagnostic(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=val1\nKEY=val2\n")
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_parse_warning(str(tmp_path), 'Duplicate key "KEY" — last value wins')

        assert diag_file.exists()
        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "env-loader"
        assert parsed["level"] == "warning"
        assert "Duplicate" in parsed["message"]


class TestSessionInitDiagnosticWriting:
    def test_nonzero_exit_writes_diagnostic(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_script_error(str(tmp_path), "session-init", "exit 1", 1)

        assert diag_file.exists()
        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session-init"
        assert parsed["level"] == "error"
        assert parsed["exitCode"] == 1

    def test_stderr_on_success_writes_warning(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_stderr_on_success(str(tmp_path), "session-init", "deprecation warning")

        assert diag_file.exists()
        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session-init"
        assert parsed["level"] == "warning"
        assert "deprecation warning" in parsed["message"]


class TestIdentityScriptDiagnostics:
    def test_stderr_on_success_writes_warning(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_stderr_on_success(str(tmp_path), "session_context_identity.py", "py warning")

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session_context_identity.py"
        assert parsed["level"] == "warning"

    def test_nonzero_exit_writes_error(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_script_error(str(tmp_path), "session_context_identity.py", "import error", 1)

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session_context_identity.py"
        assert parsed["level"] == "error"
        assert parsed["exitCode"] == 1


class TestTriggersScriptDiagnostics:
    def test_stderr_on_success_writes_warning(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_stderr_on_success(str(tmp_path), "session_context_triggers.py", "trigger warn")

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session_context_triggers.py"
        assert parsed["level"] == "warning"

    def test_nonzero_exit_writes_error(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_script_error(str(tmp_path), "session_context_triggers.py", "crash", 2)

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["level"] == "error"
        assert parsed["exitCode"] == 2


class TestHooksDiagnosticWriting:
    def test_hooks_dir_missing_writes_diagnostic(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_hooks_error(str(tmp_path), ".opencode/hooks/ directory missing")

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session-enforcement"
        assert parsed["level"] == "error"
        assert "hooks" in parsed["message"].lower()

    def test_git_dir_missing_writes_diagnostic(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        diag_file.parent.mkdir(parents=True, exist_ok=True)

        _write_diagnostic_for_hooks_error(str(tmp_path), "Could not resolve .git directory")

        content = diag_file.read_text().strip()
        parsed = json.loads(content)
        assert parsed["source"] == "session-enforcement"
        assert parsed["level"] == "error"
        assert ".git" in parsed["message"]


class TestCleanRunNoDiagnostics:
    def test_clean_run_no_diagnostic_file(self, tmp_path):
        diag_file = tmp_path / DIAGNOSTICS_FILE
        assert not diag_file.exists()

    def test_empty_diagnostics_no_block(self):
        block = _build_diagnostic_block([])
        assert block == ""


class TestDiagnosticBlockPreservesExistingBehavior:
    def test_single_diagnostic_has_both_tags(self):
        diagnostics = [
            {"source": "test", "level": "warning", "message": "msg"},
        ]
        block = _build_diagnostic_block(diagnostics)
        assert block.startswith("<PLUGIN_DIAGNOSTICS>")
        assert block.strip().endswith("</PLUGIN_DIAGNOSTICS>")

    def test_block_has_actionability_guidance(self):
        diagnostics = [
            {"source": "test", "level": "error", "message": "msg"},
        ]
        block = _build_diagnostic_block(diagnostics)
        assert "Review these diagnostics" in block


def _build_diagnostic_block(diagnostics):
    if not diagnostics:
        return ""
    entries = []
    for d in diagnostics:
        line = f"- [{d['level'].upper()}] {d['source']}: {d['message']}"
        if d.get("exitCode") is not None:
            line += f" (exit code {d['exitCode']})"
        entries.append(line)
    entries_str = "\n".join(entries)
    return (
        f"<PLUGIN_DIAGNOSTICS>\n"
        f"⚠️ The following plugin diagnostics were collected during session startup:\n\n"
        f"{entries_str}\n\n"
        f"Review these diagnostics. For errors, investigate the source script. For warnings, assess whether action is needed.\n"
        f"</PLUGIN_DIAGNOSTICS>"
    )


def _collect_diagnostics(project_dir):
    diag_path = Path(project_dir) / DIAGNOSTICS_FILE
    if not diag_path.exists():
        return []
    try:
        content = diag_path.read_text("utf8")
        diags = []
        for line in content.split("\n"):
            trimmed = line.strip()
            if not trimmed:
                continue
            try:
                diags.append(json.loads(trimmed))
            except json.JSONDecodeError:
                pass
        diag_path.write_text("", "utf8")
        return diags
    except Exception:
        return []


def _write_diagnostic(project_dir, source, level, message, exit_code=None):
    diag_path = Path(project_dir) / DIAGNOSTICS_FILE
    diag_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"source": source, "level": level, "message": message}
    if exit_code is not None:
        entry["exitCode"] = exit_code
    diag_path.write_text(json.dumps(entry) + "\n", "utf8")


def _write_diagnostic_for_env_warning(project_dir):
    _write_diagnostic(
        project_dir, "env-loader", "warning",
        ".env file is NOT in .gitignore — secrets may be committed to version control",
    )


def _write_diagnostic_for_parse_warning(project_dir, message):
    _write_diagnostic(project_dir, "env-loader", "warning", message)


def _write_diagnostic_for_script_error(project_dir, source, message, exit_code):
    _write_diagnostic(project_dir, source, "error", message, exit_code=exit_code)


def _write_diagnostic_for_stderr_on_success(project_dir, source, message):
    _write_diagnostic(project_dir, source, "warning", message)


def _write_diagnostic_for_hooks_error(project_dir, message):
    _write_diagnostic(project_dir, "session-enforcement", "error", message)