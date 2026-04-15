import os
import subprocess

import pytest


def _git_check_ignore(filepath: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", filepath],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


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