import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".opencode" / "scripts"))

from session_context_identity import (
    _parse_env_token,
    _parse_env_var_token,
    _parse_secrets_toml_token,
    build_identity_section,
    detect_platform,
    parse_owner_repo,
    probe_credentials_tier1,
    probe_credentials_tier3,
)
from session_context_identity import (
    run_git as run_git_identity,
)
from session_context_triggers import (
    build_main_branch_warning,
    build_pair_mode_resume,
    is_on_main_branch,
    is_on_protected_branch,
    is_pair_mode_branch,
)


class TestRunGitIdentity:
    def test_returns_stripped_stdout_on_success(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  hello  \n")
            result = run_git_identity(["status"])
            assert result == "hello"

    def test_returns_none_on_nonzero_exit(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            assert run_git_identity(["status"]) is None

    def test_returns_none_on_exception(self):
        with patch.object(subprocess, "run", side_effect=subprocess.SubprocessError):
            assert run_git_identity(["status"]) is None


class TestDetectPlatform:
    def test_github_https(self):
        assert detect_platform("https://github.com/owner/repo.git") == "github"

    def test_github_ssh(self):
        assert detect_platform("git@github.com:owner/repo.git") == "github"

    def test_github_without_git_suffix(self):
        assert detect_platform("https://github.com/owner/repo") == "github"


class TestParseOwnerRepo:
    def test_github_https(self):
        owner, repo = parse_owner_repo("https://github.com/MyOrg/my-repo.git", "github")
        assert owner == "MyOrg"
        assert repo == "my-repo"

    def test_github_ssh(self):
        owner, repo = parse_owner_repo("git@github.com:MyOrg/my-repo.git", "github")
        assert owner == "MyOrg"
        assert repo == "my-repo"

    def test_github_without_git_suffix(self):
        owner, repo = parse_owner_repo("https://github.com/MyOrg/my-repo", "github")
        assert owner == "MyOrg"
        assert repo == "my-repo"

    def test_gitbucket_https(self):
        owner, repo = parse_owner_repo("https://gitbucket.example.com/MyOrg/my-repo.git", "gitbucket")
        assert owner == "MyOrg"
        assert repo == "my-repo"

    def test_gitbucket_ssh(self):
        owner, repo = parse_owner_repo("git@gitbucket.example.com:MyOrg/my-repo.git", "gitbucket")
        assert owner == "MyOrg"
        assert repo == "my-repo"

    def test_unknown_platform_returns_none(self):
        owner, repo = parse_owner_repo("file:///local/repo", "unknown")
        assert owner is None
        assert repo is None


class TestParseEnvToken:
    def test_finds_token_in_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITHUB_TOKEN=ghp_abc123\n")
        result = _parse_env_token(env_file, ["GITHUB_TOKEN", "GH_TOKEN"])
        assert result == "ghp_abc123"

    def test_no_token_returns_none(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("SOME_OTHER_VAR=value\n")
        result = _parse_env_token(env_file, ["GITHUB_TOKEN"])
        assert result is None

    def test_empty_value_returns_none(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITHUB_TOKEN=\n")
        result = _parse_env_token(env_file, ["GITHUB_TOKEN"])
        assert result is None

    def test_file_not_found_returns_none(self):
        result = _parse_env_token(Path("/nonexistent/.env"), ["GITHUB_TOKEN"])
        assert result is None

    def test_quoted_values_stripped(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('GITHUB_TOKEN="ghp_quoted"\n')
        result = _parse_env_token(env_file, ["GITHUB_TOKEN"])
        assert result == "ghp_quoted"


class TestParseEnvVarToken:
    def test_finds_token_in_environ(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_env123"}):
            result = _parse_env_var_token(None, ["GITHUB_TOKEN", "GH_TOKEN"])
            assert result == "ghp_env123"

    def test_first_key_wins(self):
        with patch.dict(os.environ, {"GH_TOKEN": "ghp_first", "GITHUB_TOKEN": "ghp_second"}):
            result = _parse_env_var_token(None, ["GH_TOKEN", "GITHUB_TOKEN"])
            assert result == "ghp_first"

    def test_no_matching_env_returns_none(self):
        with patch.dict(os.environ, {}, clear=True):
            result = _parse_env_var_token(None, ["GITHUB_TOKEN"])
            assert result is None


class TestParseSecretsTomlToken:
    def test_finds_token_in_toml(self, tmp_path):
        secrets_file = tmp_path / "secrets.toml"
        secrets_file.write_text('githubtoken = "ghp_toml123"\n')
        result = _parse_secrets_toml_token(secrets_file, ["GITHUB_TOKEN"])
        assert result == "ghp_toml123"

    def test_file_not_found(self):
        result = _parse_secrets_toml_token(Path("/nonexistent/secrets.toml"), ["GITHUB_TOKEN"])
        assert result is None


class TestProbeCredentialsTier1:
    def test_returns_present_when_token_found_in_env(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITHUB_TOKEN=ghp_test\n")
        result = probe_credentials_tier1("github", str(tmp_path))
        assert result == "present"

    def test_returns_missing_when_no_token(self, tmp_path):
        result = probe_credentials_tier1("github", str(tmp_path))
        assert result == "missing"

    def test_github_platform_checks_github_keys(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITBUCKET_TOKEN=some_val\n")
        result = probe_credentials_tier1("github", str(tmp_path))
        assert result == "missing"

    def test_gitbucket_platform_checks_gitbucket_keys(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITBUCKET_TOKEN=some_val\n")
        result = probe_credentials_tier1("gitbucket", str(tmp_path))
        assert result == "present"


class TestProbeCredentialsTier3:
    def test_returns_tier1_status_if_no_probe_file(self, tmp_path):
        result = probe_credentials_tier3("github", str(tmp_path), "present")
        assert result == "present"

    def test_returns_missing_if_tier1_missing(self, tmp_path):
        probe_file = tmp_path / ".opencode-issue-probe"
        probe_file.write_text("")
        result = probe_credentials_tier3("github", str(tmp_path), "missing")
        assert result == "missing"

    def test_github_verified_with_gh_auth(self, tmp_path):
        probe_file = tmp_path / ".opencode-issue-probe"
        probe_file.write_text("")
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = probe_credentials_tier3("github", str(tmp_path), "present")
            assert result == "verified"

    def test_github_stale_when_gh_auth_fails(self, tmp_path):
        probe_file = tmp_path / ".opencode-issue-probe"
        probe_file.write_text("")
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="not logged in")
            result = probe_credentials_tier3("github", str(tmp_path), "present")
            assert result == "stale"

    def test_network_error_degrades_to_tier1_status(self, tmp_path):
        probe_file = tmp_path / ".opencode-issue-probe"
        probe_file.write_text("")
        with patch.object(subprocess, "run", side_effect=subprocess.SubprocessError):
            result = probe_credentials_tier3("github", str(tmp_path), "present")
            assert result == "present"


class TestIsOnMainBranch:
    def test_on_main(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
            assert is_on_main_branch() is True

    def test_on_dev(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            assert is_on_main_branch() is False

    def test_on_feature_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/123-xyz\n")
            assert is_on_main_branch() is False


class TestIsOnProtectedBranch:
    def test_on_main(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
            assert is_on_protected_branch() is True

    def test_on_dev(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            assert is_on_protected_branch() is True

    def test_on_feature_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/123\n")
            assert is_on_protected_branch() is False


class TestIsPairModeBranch:
    def test_pair_feature(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-feature/123-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True
            assert branch == "pair-feature/123-xyz"

    def test_pair_spec(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-spec/456-abc\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True
            assert branch == "pair-spec/456-abc"

    def test_regular_feature(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/789-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False
            assert branch is None

    def test_dev_not_pair(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False


class TestBuildIdentitySection:
    def test_github_verified(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "verified")
        assert "github.owner=MyOrg" in result
        assert "github.repo=my-repo" in result
        assert "github.platform=github" in result
        assert "GITHUB_CREDENTIALS=verified" in result

    def test_missing_credential_warning(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "missing")
        assert "WARNING" in result

    def test_stale_credential_warning(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "stale")
        assert "WARNING" in result
        assert "rejected" in result

    def test_unknown_platform(self):
        result = build_identity_section("MyOrg", "my-repo", "unknown", "unavailable")
        assert "CREDENTIALS=unavailable" in result


class TestBuildMainBranchWarning:
    def test_warning_with_changes(self):
        result = build_main_branch_warning(True, ["M file1.py", "A file2.py"])
        assert "Production Branch" in result
        assert "2 uncommitted changes" in result

    def test_warning_without_changes(self):
        result = build_main_branch_warning(False, [])
        assert "Production Branch" in result
        assert "switch to `dev`" in result


class TestBuildPairModeResume:
    def test_resume_with_issue_number(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="3 files changed\n1 insertions\n")
            result = build_pair_mode_resume("pair-feature/123-xyz")
            assert "Pair Mode Resumed" in result
            assert "#123" in result

    def test_resume_without_issue_number(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = build_pair_mode_resume("pair-feature/xyz")
            assert "Pair Mode Resumed" in result
            assert "Related issue:" not in result
