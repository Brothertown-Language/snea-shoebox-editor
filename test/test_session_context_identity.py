import os
import re
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
    run_git,
)
from session_context_identity import (
    main as identity_main,
)


def extract_value(session_output: str | None, key: str) -> str | None:
    if not session_output:
        return None
    match = re.search(rf"{re.escape(key)}=\s*(\S+)", session_output)
    return match.group(1) if match else None


class TestExtractValue:
    def test_extracts_platform(self):
        output = "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        assert extract_value(output, "github.platform") == "github"

    def test_extracts_owner(self):
        output = "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        assert extract_value(output, "github.owner") == "MyOrg"

    def test_extracts_repo(self):
        output = "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        assert extract_value(output, "github.repo") == "my-repo"

    def test_returns_none_for_missing_key(self):
        output = "## Repository Hosting Identity\n- github.platform=github"
        assert extract_value(output, "github.nonexistent") is None

    def test_returns_none_for_null_input(self):
        assert extract_value(None, "github.platform") is None

    def test_returns_none_for_empty_input(self):
        assert extract_value("", "github.platform") is None


class TestRunGit:
    def test_returns_stripped_stdout_on_success(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  hello  \n")
            result = run_git(["status"])
            assert result == "hello"

    def test_returns_none_on_nonzero_exit(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            assert run_git(["status"]) is None

    def test_returns_none_on_exception(self):
        with patch.object(subprocess, "run", side_effect=subprocess.SubprocessError):
            assert run_git(["status"]) is None


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

    def test_gitbucket_https(self):
        owner, repo = parse_owner_repo("https://gitbucket.example.com/MyOrg/my-repo.git", "gitbucket")
        assert owner == "MyOrg"
        assert repo == "my-repo"


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


class TestParseEnvVarToken:
    def test_finds_token_in_environ(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_env123"}):
            result = _parse_env_var_token(None, ["GITHUB_TOKEN", "GH_TOKEN"])
            assert result == "ghp_env123"

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


class TestProbeCredentialsTier1:
    def test_returns_present_when_token_found(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GITHUB_TOKEN=ghp_test\n")
        result = probe_credentials_tier1("github", str(tmp_path))
        assert result == "present"

    def test_returns_missing_when_no_token(self, tmp_path):
        result = probe_credentials_tier1("github", str(tmp_path))
        assert result == "missing"


class TestProbeCredentialsTier3:
    def test_returns_tier1_if_no_probe_file(self, tmp_path):
        result = probe_credentials_tier3("github", str(tmp_path), "present")
        assert result == "present"

    def test_github_verified(self, tmp_path):
        probe_file = tmp_path / ".opencode-issue-probe"
        probe_file.write_text("")
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = probe_credentials_tier3("github", str(tmp_path), "present")
            assert result == "verified"


class TestBuildIdentitySection:
    def test_github_verified(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "verified")
        assert "github.owner=MyOrg" in result
        assert "github.repo=my-repo" in result
        assert "github.platform=github" in result
        assert "GITHUB_CREDENTIALS=verified" in result

    def test_repository_hosting_identity_header(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "verified")
        assert "## Repository Hosting Identity" in result

    def test_target_api_credentials_section(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "verified")
        assert "## Target API Credentials" in result
        assert "Do NOT infer the hosting platform from these values" in result

    def test_missing_credential_warning(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "missing")
        assert "WARNING" in result

    def test_unknown_platform(self):
        result = build_identity_section("MyOrg", "my-repo", "unknown", "unavailable")
        assert "CREDENTIALS=unavailable" in result

    def test_hosting_and_target_sections_separated(self):
        result = build_identity_section("TestOrg", "test-repo", "github", "present")
        hosting_idx = result.index("## Repository Hosting Identity")
        target_idx = result.index("## Target API Credentials")
        assert hosting_idx < target_idx


class TestIdentityOnlyOutput:
    def test_identity_only_output(self, tmp_path):
        with (
            patch("session_context_identity.get_remote_url", return_value="https://github.com/MyOrg/my-repo.git"),
            patch("session_context_identity.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_identity.probe_credentials_tier1", return_value="present"),
            patch("session_context_identity.probe_credentials_tier3", return_value="present"),
            patch("sys.stdout") as mock_stdout,
        ):
            identity_main()
        output = "".join(c[0][0] for c in mock_stdout.write.call_args_list)
        assert "## Repository Hosting Identity" in output

    def test_credential_status_present(self, tmp_path, capsys):
        with (
            patch("session_context_identity.get_remote_url", return_value="https://github.com/MyOrg/my-repo.git"),
            patch("session_context_identity.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_identity.probe_credentials_tier1", return_value="present"),
            patch("session_context_identity.probe_credentials_tier3", return_value="present"),
        ):
            identity_main()
        captured = capsys.readouterr()
        assert "GITHUB_CREDENTIALS=present" in captured.out

    def test_credential_status_missing(self, tmp_path, capsys):
        with (
            patch("session_context_identity.get_remote_url", return_value="https://github.com/MyOrg/my-repo.git"),
            patch("session_context_identity.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_identity.probe_credentials_tier1", return_value="missing"),
            patch("session_context_identity.probe_credentials_tier3", return_value="missing"),
        ):
            identity_main()
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_no_triggers_in_output(self, tmp_path, capsys):
        with (
            patch("session_context_identity.get_remote_url", return_value="https://github.com/MyOrg/my-repo.git"),
            patch("session_context_identity.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_identity.probe_credentials_tier1", return_value="present"),
            patch("session_context_identity.probe_credentials_tier3", return_value="present"),
        ):
            identity_main()
        captured = capsys.readouterr()
        assert "on_main_branch" not in captured.out
        assert "Uncommitted Work" not in captured.out
        assert "Merge Conflict" not in captured.out
        assert "Stale Stash" not in captured.out
        assert "Unpushed Commits" not in captured.out
        assert "Orphaned Worktrees" not in captured.out
        assert "Pair Mode" not in captured.out
        assert "Protected Branch" not in captured.out

    def test_exit_code_0(self, tmp_path):
        with (
            patch("session_context_identity.get_remote_url", return_value="https://github.com/MyOrg/my-repo.git"),
            patch("session_context_identity.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_identity.probe_credentials_tier1", return_value="present"),
            patch("session_context_identity.probe_credentials_tier3", return_value="present"),
        ):
            assert identity_main() == 0

    def test_exit_code_1_no_remote(self, tmp_path):
        with patch("session_context_identity.get_remote_url", return_value=None):
            assert identity_main() == 1


class TestIdentityEchoValidation:
    ECHO_PATTERN = re.compile(r"Platform:\s*(\S+),\s*Org:\s*(\S+),\s*Repo:\s*(\S+)")

    def test_echo_match_no_failure(self):
        known_output = (
            "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        )
        known_platform = extract_value(known_output, "github.platform")
        known_owner = extract_value(known_output, "github.owner")
        known_repo = extract_value(known_output, "github.repo")

        assistant_text = "Platform: github, Org: MyOrg, Repo: my-repo\n🤖 OpenCode (ollama-cloud/glm-5) ✅ ready"
        match = self.ECHO_PATTERN.search(assistant_text)

        assert match is not None
        echo_platform, echo_owner, echo_repo = match.group(1), match.group(2), match.group(3)
        assert echo_platform == known_platform
        assert echo_owner == known_owner
        assert echo_repo == known_repo

    def test_echo_mismatch_injects_failure(self):
        known_output = (
            "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        )
        known_platform = extract_value(known_output, "github.platform")
        known_owner = extract_value(known_output, "github.owner")
        known_repo = extract_value(known_output, "github.repo")

        assistant_text = "Platform: github, Org: WrongOrg, Repo: wrong-repo\n🤖 OpenCode (ollama-cloud/glm-5) ✅ ready"
        match = self.ECHO_PATTERN.search(assistant_text)

        assert match is not None
        echo_platform, echo_owner, echo_repo = match.group(1), match.group(2), match.group(3)
        mismatch = echo_platform != known_platform or echo_owner != known_owner or echo_repo != known_repo
        assert mismatch

        failure_block = (
            f"<IDENTITY_VALIDATION_FAILURE>\n"
            f"⚠️ FATAL: Identity echo mismatch detected!\n\n"
            f"Your echo: Platform: {echo_platform}, Org: {echo_owner}, Repo: {echo_repo}\n"
            f"Expected: Platform: {known_platform}, Org: {known_owner}, Repo: {known_repo}\n\n"
            f"HALT all operations. These values do NOT match. "
            f"Use ONLY the expected values above. Do NOT infer identity from repository names, "
            f"file paths, or environment variables.\n"
            f"</IDENTITY_VALIDATION_FAILURE>"
        )
        assert "IDENTITY_VALIDATION_FAILURE" in failure_block
        assert "mismatch detected" in failure_block
        assert f"Your echo: Platform: {echo_platform}" in failure_block
        assert f"Expected: Platform: {known_platform}" in failure_block

    def test_missing_echo_injects_failure(self):
        known_output = (
            "## Repository Hosting Identity\n- github.platform=github\n- github.owner=MyOrg\n- github.repo=my-repo"
        )
        known_platform = extract_value(known_output, "github.platform")
        known_owner = extract_value(known_output, "github.owner")
        known_repo = extract_value(known_output, "github.repo")

        assistant_text = "I will help you with that task."
        match = self.ECHO_PATTERN.search(assistant_text)

        assert match is None

        failure_block = (
            f"<IDENTITY_VALIDATION_FAILURE>\n"
            f"⚠️ FATAL: Your first message did not contain a valid identity echo. "
            f"You MUST echo your platform identity before proceeding with ANY operations.\n\n"
            f"Expected: Platform: {known_platform}, Org: {known_owner}, Repo: {known_repo}\n\n"
            f"HALT all operations. Echo the correct identity values above before continuing.\n"
            f"</IDENTITY_VALIDATION_FAILURE>"
        )
        assert "IDENTITY_VALIDATION_FAILURE" in failure_block
        assert "did not contain a valid identity echo" in failure_block
        assert f"Expected: Platform: {known_platform}" in failure_block

    def test_credential_target_separation(self):
        result = build_identity_section("MyOrg", "my-repo", "github", "verified")
        lines = result.split("\n")

        hosting_idx = None
        target_idx = None
        for i, line in enumerate(lines):
            if "## Repository Hosting Identity" in line:
                hosting_idx = i
            if "## Target API Credentials" in line:
                target_idx = i

        assert hosting_idx is not None
        assert target_idx is not None
        assert hosting_idx < target_idx

        hosting_lines = lines[hosting_idx:target_idx]
        hosting_text = "\n".join(hosting_lines)
        assert "github.owner=MyOrg" in hosting_text
        assert "github.repo=my-repo" in hosting_text
        assert "github.platform=github" in hosting_text

        target_lines = lines[target_idx:]
        target_text = "\n".join(target_lines)
        assert "Do NOT infer the hosting platform from these values" in target_text
