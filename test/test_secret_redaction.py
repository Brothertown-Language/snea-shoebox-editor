"""
Tests for secret redaction guard rails (Phase 2 of #1152/#1154).

Covers:
- R1: redactSecrets() in TypeScript (tested via Python equivalent logic)
- R2: scan_content() from pre_submission_scan.py
- R3: is_blocklisted() and redact_file_content() from file_read_blocklist.py
- R4: 000-critical-rules.md contains "Secret Exfiltration in Agent Output" section
- SC1-SC14: Success criteria from spec #1154
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from security.file_read_blocklist import (
    BLOCKLIST_PATTERNS,
    is_blocklisted,
    redact_file_content,
)
from security.pre_submission_scan import (
    check_baseline,
    redact_content,
    scan_content,
)

CRITICAL_RULES_PATH = Path(__file__).resolve().parent.parent / ".opencode" / "guidelines" / "000-critical-rules.md"


class TestRedactSecretsLogic:
    """Tests for the redaction logic that mirrors session-enforcement.ts redactSecrets()."""

    def _redact_like_ts(self, text: str) -> str:
        """Python equivalent of the TypeScript redactSecrets function."""
        result = text

        # URL-embedded passwords
        result = re.sub(
            r"://([^:]+):([^@]+)@",
            lambda m: f"://{m.group(1)}:[REDACTED:PASSWORD]@",
            result,
        )

        # GitHub tokens
        result = re.sub(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}", "[REDACTED:TOKEN]", result)

        # GitLab tokens
        result = re.sub(r"\bglpat-[A-Za-z0-9\-]{20,}", "[REDACTED:TOKEN]", result)

        # Assignment patterns: matches keys ending with or being exactly TOKEN/KEY/etc.
        # e.g., GITBUCKET_TOKEN=value, MY_SECRET=value, PASSWORD=abc, API_KEY="xyz"
        def _replace_assignment(m: re.Match) -> str:
            prefix = m.group(1)
            quote = m.group(2)
            key_match = re.match(r"(\w+)\s*[=?:]", prefix)
            key_name = key_match.group(1).upper() if key_match else ""
            if key_name == "PASSWORD" or key_name.endswith("PASSWORD"):
                type_label = "PASSWORD"
            elif key_name == "CREDENTIAL" or key_name.endswith("CREDENTIAL"):
                type_label = "CREDENTIAL"
            else:
                type_label = "TOKEN"
            return f"{prefix}{quote}[REDACTED:{type_label}]{quote}"

        result = re.sub(
            r'((?:\w*(?:TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL|API_KEY|PRIVATE_KEY|ACCESS_TOKEN))\s*[=:]\s*)(["\']?)([^\s"\'#]+?)\2',
            _replace_assignment,
            result,
            flags=re.IGNORECASE,
        )

        return result

    def test_sc1_token_assignment_redacted(self):
        """SC1: GITBUCKET_TOKEN=abc123def → GITBUCKET_TOKEN=[REDACTED:TOKEN]"""
        result = self._redact_like_ts("GITBUCKET_TOKEN=abc123def")
        assert "[REDACTED:TOKEN]" in result
        assert "abc123def" not in result
        assert "GITBUCKET_TOKEN=" in result

    def test_sc2_quoted_password_redacted(self):
        """SC2: PASSWORD="s3cret" → PASSWORD="[REDACTED:PASSWORD]" """
        result = self._redact_like_ts('PASSWORD="s3cret"')
        assert "[REDACTED:PASSWORD]" in result
        assert "s3cret" not in result

    def test_sc3_multiline_env_redacted(self):
        """SC3: Full .env file content with 5+ key-value pairs redacted, keys preserved."""
        env_content = """DATABASE_HOST=localhost
DATABASE_PORT=5432
API_KEY=sk_live_abc123def456
SECRET=supersecretvalue
TOKEN=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ
PASSWORD=mypassword123
ACCESS_TOKEN=github_token_value"""
        result = self._redact_like_ts(env_content)
        assert "API_KEY=[REDACTED:TOKEN]" in result
        assert "SECRET=[REDACTED:TOKEN]" in result
        assert "TOKEN=[REDACTED:TOKEN]" in result
        assert "PASSWORD=[REDACTED:PASSWORD]" in result
        assert "ACCESS_TOKEN=[REDACTED:TOKEN]" in result
        assert "DATABASE_HOST=localhost" in result
        assert "DATABASE_PORT=5432" in result
        assert "sk_live_abc123def456" not in result
        assert "supersecretvalue" not in result
        assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in result

    def test_sc4_url_embedded_password_redacted(self):
        """SC4: https://user:p@ssw0rd@host → https://user:[REDACTED:PASSWORD]@host"""
        result = self._redact_like_ts("https://user:p@ssw0rd@host.example.com")
        assert "[REDACTED:PASSWORD]" in result
        assert "p@ssw0rd" not in result
        assert "user:" in result

    def test_case_insensitive_matching(self):
        """Key names are matched case-insensitively."""
        result = self._redact_like_ts("token=mysecretvalue")
        assert "[REDACTED:TOKEN]" in result
        assert "mysecretvalue" not in result

    def test_key_names_preserved(self):
        """Key names must be preserved — only values are redacted."""
        result = self._redact_like_ts("MY_SECRET_KEY=secretvalue123")
        assert "MY_SECRET_KEY=" in result
        assert "secretvalue123" not in result
        assert "[REDACTED:TOKEN]" in result

    def test_github_token_standalone_redacted(self):
        """Standalone GitHub tokens (ghp_, gho_, etc.) are redacted."""
        result = self._redact_like_ts("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345")
        assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345" not in result
        assert "[REDACTED:TOKEN]" in result

    def test_gitlab_token_redacted(self):
        """Stalone GitLab tokens (glpat-) are redacted."""
        result = self._redact_like_ts("glpat-ABCDEFGHIJKLMNOPQRSTUVWXYZ01234")
        assert "glpat-" not in result or "[REDACTED:TOKEN]" in result
        assert "[REDACTED:TOKEN]" in result

    def test_single_quoted_value_redacted(self):
        """Single-quoted values after secret keys are redacted."""
        result = self._redact_like_ts("TOKEN='mysecrettoken'")
        assert "[REDACTED:TOKEN]" in result
        assert "mysecrettoken" not in result


class TestScanContent:
    """Tests for pre_submission_scan.scan_content()."""

    def test_detects_token_assignment(self):
        findings = scan_content("GITBUCKET_TOKEN=abc123def")
        assert len(findings) >= 1
        assert findings[0]["type"] == "secret_pattern"
        assert "TOKEN" in findings[0]["match"].upper()

    def test_detects_github_token(self):
        findings = scan_content("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345")
        assert len(findings) >= 1
        assert any("ghp" in f["match"] for f in findings)

    def test_detects_gitlab_token(self):
        findings = scan_content("glpat-ABCDEFGHIJKLMNOPQRSTUVWXYZ01234")
        assert len(findings) >= 1
        assert any("glpat" in f["match"] for f in findings)

    def test_clean_content_no_findings(self):
        """SC6: Clean content passes through without findings."""
        findings = scan_content("This is a clean comment with no secrets.")
        assert len(findings) == 0

    def test_multiline_with_secrets(self):
        content = "Some text\nAPI_KEY=sk_live_abc\nMore text"
        findings = scan_content(content)
        assert len(findings) >= 1

    def test_line_numbers_are_correct(self):
        content = "line one\nAPI_KEY=secret\nline three"
        findings = scan_content(content)
        assert any(f["line"] == 2 for f in findings)


class TestRedactContent:
    """Tests for pre_submission_scan.redact_content()."""

    def test_redacts_token(self):
        result = redact_content("TOKEN=mysecretvalue")
        assert "mysecretvalue" not in result
        assert "[REDACTED]" in result

    def test_preserves_non_secret(self):
        result = redact_content("This is normal text without secrets")
        assert "This is normal text without secrets" == result


class TestCheckBaseline:
    """Tests for pre_submission_scan.check_baseline()."""

    def test_baseline_not_found(self, tmp_path):
        result = check_baseline(tmp_path / "nonexistent.baseline")
        assert result is False

    def test_baseline_found(self, tmp_path):
        baseline = tmp_path / ".secrets.baseline"
        baseline.write_text("{}")
        result = check_baseline(baseline)
        assert result is True


class TestIsBlocklisted:
    """Tests for file_read_blocklist.is_blocklisted()."""

    def test_sc7_env_file_is_blocklisted(self):
        """SC7: .env triggers redaction."""
        assert is_blocklisted(".env") is True

    def test_sc8_env_production_is_blocklisted(self):
        """SC8: .env.production (glob match) triggers redaction."""
        assert is_blocklisted(".env.production") is True

    def test_env_local_is_blocklisted(self):
        """SC8 variant: .env.local triggers redaction."""
        assert is_blocklisted(".env.local") is True

    def test_sc9_secrets_toml_blocklisted(self):
        """SC9: config/secrets.toml triggers redaction (basename match)."""
        assert is_blocklisted("config/secrets.toml") is True

    def test_pem_file_is_blocklisted(self):
        assert is_blocklisted("server.pem") is True

    def test_key_file_is_blocklisted(self):
        assert is_blocklisted("ssh.key") is True

    def test_credentials_json_blocklisted(self):
        assert is_blocklisted("credentials.json") is True

    def test_sc10_main_py_not_blocklisted(self):
        """SC10: src/main.py does NOT trigger redaction."""
        assert is_blocklisted("src/main.py") is False

    def test_regular_files_not_blocklisted(self):
        assert is_blocklisted("app.py") is False
        assert is_blocklisted("config.yaml") is False
        assert is_blocklisted("README.md") is False

    def test_blocklist_patterns_defined(self):
        assert len(BLOCKLIST_PATTERNS) >= 6


class TestRedactFileContent:
    """Tests for file_read_blocklist.redact_file_content()."""

    def test_sc11_secrets_redacted_header(self):
        """SC11: Blocklisted file content includes ⚠️ SECRETS REDACTED header."""
        content = "TOKEN=abc123\nDATABASE_HOST=localhost"
        result = redact_file_content(content)
        assert "⚠️ SECRETS REDACTED" in result
        assert "[REDACTED:TYPE]" in result or "[REDACTED]" in result

    def test_key_names_preserved(self):
        """Key names are preserved, only values are redacted."""
        content = "MY_TOKEN=secretvalue123\nPASSWORD=hunter2"
        result = redact_file_content(content)
        assert "MY_TOKEN" in result
        assert "PASSWORD" in result
        assert "secretvalue123" not in result
        assert "hunter2" not in result

    def test_multi_line_env_redaction(self):
        content = """DATABASE_URL=postgres://user:pass@localhost:5432/db
API_KEY=sk_live_abc123
SECRET=supersecret
"""
        result = redact_file_content(content)
        assert "DATABASE_URL" in result
        assert "API_KEY" in result
        assert "SECRET" in result
        assert "sk_live_abc123" not in result
        assert "supersecret" not in result

    def test_header_appears_at_start(self):
        content = "TOKEN=value"
        result = redact_file_content(content)
        assert result.startswith("⚠️ SECRETS REDACTED")

    def test_url_password_redaction(self):
        content = "DATABASE_URL=postgres://admin:secretpass@localhost/db"
        result = redact_file_content(content)
        assert "[REDACTED:PASSWORD]" in result or "[REDACTED]" in result
        assert "secretpass" not in result

    def test_empty_file_produces_header(self):
        result = redact_file_content("")
        assert "⚠️ SECRETS REDACTED" in result


class TestSecretExfiltrationRule:
    """Tests for the critical violation section in 000-critical-rules.md."""

    def test_sc12_section_exists(self):
        """SC12: 000-critical-rules.md contains 'Secret Exfiltration in Agent Output' section."""
        content = CRITICAL_RULES_PATH.read_text()
        assert "Secret Exfiltration in Agent Output" in content

    def test_sc13_covers_all_channels(self):
        """SC13: The rule covers issue comments, PR descriptions, commit messages, and chat."""
        content = CRITICAL_RULES_PATH.read_text()
        secret_section_start = content.find("Secret Exfiltration in Agent Output")
        assert secret_section_start != -1, "Secret Exfiltration section not found"
        section = content.lower()
        assert "issue comments" in section or "issue comment" in section
        assert "pr descriptions" in section or "pr description" in section
        assert "commit messages" in section or "commit message" in section
        assert "chat" in section

    def test_section_is_critical_violation(self):
        """The section is marked as a Critical Violation."""
        content = CRITICAL_RULES_PATH.read_text()
        secret_section_start = content.find("Secret Exfiltration in Agent Output")
        assert secret_section_start != -1
        section = content[secret_section_start : secret_section_start + 2000]
        assert "CRITICAL GUIDELINE VIOLATION" in section or "Critical Violation" in section

    def test_forbidden_includes_env_contents(self):
        """The FORBIDDEN list includes .env file contents."""
        content = CRITICAL_RULES_PATH.read_text()
        secret_section_start = content.find("Secret Exfiltration in Agent Output")
        section = content[secret_section_start : secret_section_start + 3000]
        assert ".env" in section

    def test_required_includes_redaction(self):
        """The REQUIRED list includes redaction to [REDACTED]."""
        content = CRITICAL_RULES_PATH.read_text()
        secret_section_start = content.find("Secret Exfiltration in Agent Output")
        section = content[secret_section_start : secret_section_start + 3000]
        assert "[REDACTED]" in section
