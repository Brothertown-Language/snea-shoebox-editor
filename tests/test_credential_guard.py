import importlib.util
import os
import subprocess
import tempfile

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git_check_ignore(filepath: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", filepath],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _load_session_init():
    script_path = os.path.join(REPO_ROOT, ".opencode", "tools", "session-init")
    spec = importlib.util.spec_from_file_location("session_init", script_path)
    assert spec is not None and spec.loader is not None, f"Cannot load session-init from {script_path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGitignoreCredentialCoverage:
    CREDENTIAL_FILENAMES = [
        ".env",
        ".env.local",
        ".env.production",
        "secrets.toml",
        "secrets.toml.production",
        ".streamlit/secrets.toml",
        ".streamlit/secrets.toml.production",
        "service-account.json",
        "credentials.json",
        "gcloud-credentials.json",
        "id_rsa",
        "id_ed25519",
        "server.key",
        "server.pem",
        "client.p12",
        "backup-credentials.yaml",
    ]

    @pytest.mark.parametrize("filepath", CREDENTIAL_FILENAMES)
    def test_credential_file_is_gitignored(self, filepath: str):
        assert _git_check_ignore(filepath), f"{filepath} is NOT matched by .gitignore"


class TestPreCommitSecretScanning:
    def test_detect_secrets_hook_is_local(self):
        with open(".pre-commit-config.yaml") as f:
            config = yaml.safe_load(f)
        local_repo = None
        for repo in config.get("repos", []):
            if repo.get("repo") == "local":
                local_repo = repo
                break
        assert local_repo is not None, "No local repo found in .pre-commit-config.yaml"
        hook_ids = [h.get("id") for h in local_repo.get("hooks", [])]
        assert "detect-secrets" in hook_ids, f"detect-secrets hook not found in local repo. Found: {hook_ids}"

    def test_detect_secrets_wrapper_skips_without_baseline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env.pop("PRE_COMMIT", None)
            result = subprocess.run(
                [os.path.join(REPO_ROOT, ".opencode", "tools", "detect-secrets-wrapper.sh")],
                capture_output=True,
                text=True,
                env=env,
                cwd=tmpdir,
            )
            assert result.returncode == 0, (
                f"Wrapper should exit 0 in empty dir (no baseline), got {result.returncode}. stderr: {result.stderr}"
            )

    def test_secrets_baseline_is_gitignored(self):
        assert _git_check_ignore(".secrets.baseline"), ".secrets.baseline is NOT matched by .gitignore"


class TestSessionInitCredentialGuard:
    def test_credential_check_function_exists(self):
        with open(os.path.join(REPO_ROOT, ".opencode", "tools", "session-init")) as f:
            source = f.read()
        assert "_check_credential_files_gitignored" in source, (
            "_check_credential_files_gitignored function not found in session-init"
        )
        assert "CREDENTIAL_FILE_PATTERNS" in source, "CREDENTIAL_FILE_PATTERNS list not found in session-init"
        assert ".streamlit/secrets.toml" in source, ".streamlit/secrets.toml not referenced in credential patterns"
        assert ".streamlit/secrets.toml.production" in source, (
            ".streamlit/secrets.toml.production not referenced in credential patterns"
        )

    def test_run_guard_checks_uses_credential_function(self):
        with open(os.path.join(REPO_ROOT, ".opencode", "tools", "session-init")) as f:
            source = f.read()
        assert "_check_credential_files_gitignored()" in source, (
            "run_guard_checks does not call _check_credential_files_gitignored"
        )


class TestIntegrationGuard:
    _SECRET_PATTERNS = [
        "*.env",
        "*.key",
        "*.pem",
        "*.p12",
        "*secret*",
        "*credential*",
        "*service-account*",
    ]

    def test_no_secret_files_git_tracked(self):
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        tracked_files = result.stdout.strip().splitlines()
        violations = []
        for f in tracked_files:
            basename = os.path.basename(f).lower()
            for pattern in self._SECRET_PATTERNS:
                pattern_stem = pattern.lstrip("*").lower()
                if pattern_stem in basename and not f.startswith("tests/"):
                    if "test_credential_guard" not in f and "credential-leakage-remediation" not in f:
                        violations.append(f)
        assert violations == [], f"Secret-like files are git-tracked: {violations}"

    def test_pre_commit_config_references_wrapper(self):
        with open(os.path.join(REPO_ROOT, ".pre-commit-config.yaml")) as f:
            config = yaml.safe_load(f)
        hook_entry = None
        for repo in config.get("repos", []):
            for hook in repo.get("hooks", []):
                if hook.get("id") == "detect-secrets":
                    hook_entry = hook
                    break
        assert hook_entry is not None, "detect-secrets hook not found in pre-commit config"
        assert hook_entry.get("entry", "").endswith("detect-secrets-wrapper.sh"), (
            f"detect-secrets hook entry does not reference wrapper script: {hook_entry.get('entry')}"
        )

    def test_wrapper_script_is_executable(self):
        wrapper = os.path.join(REPO_ROOT, ".opencode", "tools", "detect-secrets-wrapper.sh")
        assert os.access(wrapper, os.X_OK), f"{wrapper} is not executable"

    def test_remediation_doc_exists(self):
        doc_path = os.path.join(REPO_ROOT, "docs", "security", "credential-leakage-remediation.md")
        assert os.path.isfile(doc_path), f"Remediation doc not found at {doc_path}"
