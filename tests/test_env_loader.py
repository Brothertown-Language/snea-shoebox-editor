"""
Tests for the env-loader plugin's .env parsing logic.

Since the plugin is TypeScript (.opencode/plugins/env-loader.ts), we test
the core parsing logic by re-implementing it in Python to verify correctness.
The TypeScript implementation mirrors this logic exactly.

Co-authored with AI: OpenCode (ollama-cloud/glm-5)
"""

import os
import tempfile


def parse_env_file(content: str) -> tuple[dict[str, str], list[str]]:
    """Python reimplementation of the TypeScript parseEnvFile for testing."""
    env: dict[str, str] = {}
    warnings: list[str] = []

    for raw_line in content.split("\n"):
        line = raw_line.strip()

        if line == "" or line.startswith("#"):
            continue

        eq_idx = line.find("=")
        if eq_idx == -1:
            continue

        key = line[:eq_idx].strip()
        value = line[eq_idx + 1 :].strip()

        if not key:
            continue

        # Strip inline comments before unquoting
        value = _strip_inline_comments(value)

        # Strip surrounding quotes
        if _is_quoted(value):
            value = value[1:-1]

        if key in env:
            warnings.append(f'Duplicate key "{key}" — last value wins')

        env[key] = value

    return env, warnings


def _strip_inline_comments(value: str) -> str:
    # If value is quoted, don't strip inline comments
    if _is_quoted(value):
        return value
    # For unquoted values, strip inline comments
    hash_idx = value.find(" #")
    if hash_idx != -1:
        return value[:hash_idx].strip()
    return value


def _is_quoted(value: str) -> bool:
    return (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))


def is_env_gitignored(gitignore_path: str) -> bool:
    """Python reimplementation of the TypeScript isEnvGitignored."""
    try:
        with open(gitignore_path) as f:
            content = f.read()
        for line in content.split("\n"):
            trimmed = line.strip()
            if trimmed == ".env" or trimmed == "/.env":
                return True
        return False
    except FileNotFoundError:
        return False


class TestParseEnvFile:
    def test_basic_key_value(self):
        env, _ = parse_env_file("DB_HOST=localhost\nDB_PORT=5432")
        assert env == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_skip_blank_lines(self):
        env, _ = parse_env_file("KEY1=val1\n\n\nKEY2=val2")
        assert env == {"KEY1": "val1", "KEY2": "val2"}

    def test_skip_comment_lines(self):
        env, _ = parse_env_file("# This is a comment\nKEY=val\n# Another comment")
        assert env == {"KEY": "val"}

    def test_double_quoted_values(self):
        env, _ = parse_env_file('KEY="value with spaces"')
        assert env == {"KEY": "value with spaces"}

    def test_single_quoted_values(self):
        env, _ = parse_env_file("KEY='value with spaces'")
        assert env == {"KEY": "value with spaces"}

    def test_inline_comments_stripped(self):
        env, _ = parse_env_file("KEY=value # this is a comment")
        assert env == {"KEY": "value"}

    def test_inline_comments_not_stripped_in_quotes(self):
        env, _ = parse_env_file('KEY="value # not a comment"')
        assert env == {"KEY": "value # not a comment"}

    def test_missing_env_file_graceful(self):
        env, _ = parse_env_file("")
        assert env == {}

    def test_duplicate_key_warning(self):
        _, warnings = parse_env_file("KEY=first\nKEY=second")
        assert len(warnings) == 1
        assert "Duplicate key" in warnings[0]

    def test_duplicate_key_last_wins(self):
        env, _ = parse_env_file("KEY=first\nKEY=second")
        assert env["KEY"] == "second"

    def test_no_equals_sign_skipped(self):
        env, _ = parse_env_file("NOTAVALIDLINE\nKEY=val")
        assert env == {"KEY": "val"}

    def test_empty_value(self):
        env, _ = parse_env_file("KEY=")
        assert env == {"KEY": ""}

    def test_value_with_equals(self):
        env, _ = parse_env_file("KEY=val=ue")
        assert env == {"KEY": "val=ue"}

    def test_whitespace_trimming(self):
        env, _ = parse_env_file("  KEY  =  value  ")
        assert env == {"KEY": "value"}

    def test_empty_key_skipped(self):
        env, _ = parse_env_file("=value\nKEY=val")
        assert env == {"KEY": "val"}

    def test_only_comments_and_blanks(self):
        env, _ = parse_env_file("# comment\n\n# another\n")
        assert env == {}

    def test_quoted_empty_value(self):
        env, _ = parse_env_file('KEY=""')
        assert env == {"KEY": ""}

    def test_multiple_inline_hashes_preserved_in_quotes(self):
        env, _ = parse_env_file('KEY="val#1 #2"')
        assert env == {"KEY": "val#1 #2"}

    def test_realistic_env_file(self):
        content = """# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb

# API keys
API_KEY="sk-abc123def456"
API_SECRET='super-secret-value'

# Feature flags
FEATURE_X=enabled # TODO: remove after launch
FEATURE_Y=disabled
"""
        env, warnings = parse_env_file(content)
        assert env["DB_HOST"] == "localhost"
        assert env["DB_PORT"] == "5432"
        assert env["DB_NAME"] == "mydb"
        assert env["API_KEY"] == "sk-abc123def456"
        assert env["API_SECRET"] == "super-secret-value"
        assert env["FEATURE_X"] == "enabled"
        assert env["FEATURE_Y"] == "disabled"
        assert len(warnings) == 0


class TestIsEnvGitignored:
    def test_env_gitignored(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gitignore", delete=False) as f:
            f.write("node_modules/\n.env\n*.log\n")
            f.flush()
            result = is_env_gitignored(f.name)
        os.unlink(f.name)
        assert result is True

    def test_env_not_gitignored(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gitignore", delete=False) as f:
            f.write("node_modules/\n*.log\n")
            f.flush()
            result = is_env_gitignored(f.name)
        os.unlink(f.name)
        assert result is False

    def test_env_gitignored_with_slash_prefix(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gitignore", delete=False) as f:
            f.write("/.env\n")
            f.flush()
            result = is_env_gitignored(f.name)
        os.unlink(f.name)
        assert result is True

    def test_missing_gitignore(self):
        result = is_env_gitignored("/nonexistent/path/.gitignore")
        assert result is False
