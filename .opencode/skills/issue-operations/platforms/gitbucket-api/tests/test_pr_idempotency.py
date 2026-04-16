import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from gitbucket_api import GitBucketAPI


def _make_api() -> GitBucketAPI:
    with patch.object(GitBucketAPI, "__init__", lambda self, **kw: None):
        api = GitBucketAPI.__new__(GitBucketAPI)
        api.url = "https://gitbucket.example.com/api/v3/"
        api.auth = MagicMock()
        api.auth.get_headers.return_value = {"Content-Type": "application/json"}
        return api


def test_list_pull_requests_with_head_param():
    api = _make_api()
    api._request = MagicMock(return_value=[
        {"number": 1, "head": {"ref": "feature/X", "label": "feature/X"}, "state": "open"},
        {"number": 2, "head": {"ref": "feature/Y", "label": "feature/Y"}, "state": "open"},
    ])
    result = api.list_pull_requests("owner", "repo", state="open", head="feature/X")
    call_args = api._request.call_args
    params = call_args[1].get("params") or call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get("params")
    assert params is not None
    assert params.get("head") == "feature/X"


def test_create_pull_request_idempotent_returns_existing():
    api = _make_api()
    existing_pr = {
        "number": 42,
        "head": {"ref": "feature/X", "label": "feature/X"},
        "state": "open",
        "html_url": "https://gitbucket.example.com/owner/repo/pull/42",
    }
    api.list_pull_requests = MagicMock(return_value=[existing_pr])
    api._request = MagicMock()
    result = api.create_pull_request("owner", "repo", "Title", "feature/X", "dev")
    assert result["number"] == 42
    api._request.assert_not_called()


def test_create_pull_request_creates_when_no_existing():
    api = _make_api()
    api.list_pull_requests = MagicMock(return_value=[])
    new_pr = {
        "number": 99,
        "head": {"ref": "feature/new", "label": "feature/new"},
        "state": "open",
        "html_url": "https://gitbucket.example.com/owner/repo/pull/99",
    }
    api._request = MagicMock(return_value=new_pr)
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(Path, "cwd", return_value=Path(tmp)):
            result = api.create_pull_request("owner", "repo", "Title", "feature/new", "dev")
    assert result["number"] == 99
    api._request.assert_called_once()


def test_create_pull_request_persists_response():
    api = _make_api()
    api.list_pull_requests = MagicMock(return_value=[])
    new_pr = {
        "number": 55,
        "head": {"ref": "feature/persist", "label": "feature/persist"},
        "state": "open",
        "html_url": "https://gitbucket.example.com/owner/repo/pull/55",
    }
    api._request = MagicMock(return_value=new_pr)
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(Path, "cwd", return_value=Path(tmp)):
            api.create_pull_request("owner", "repo", "Title", "feature/persist", "dev")
            pr_file = Path(tmp) / "tmp" / "pr-response.json"
            assert pr_file.exists()
            data = json.loads(pr_file.read_text(encoding="utf-8"))
            assert isinstance(data, list)
            assert data[-1]["number"] == 55


def test_create_pull_request_no_duplicate_on_same_head():
    api = _make_api()
    existing_pr = {
        "number": 10,
        "head": {"ref": "feature/dup", "label": "feature/dup"},
        "state": "open",
    }
    api.list_pull_requests = MagicMock(return_value=[existing_pr])
    api._request = MagicMock()
    result1 = api.create_pull_request("owner", "repo", "Title", "feature/dup", "dev")
    result2 = api.create_pull_request("owner", "repo", "Title", "feature/dup", "dev")
    assert result1["number"] == result2["number"] == 10
    api._request.assert_not_called()


def test_list_pull_requests_head_param_sent_to_api():
    api = _make_api()
    api._request = MagicMock(return_value=[])
    api.list_pull_requests("owner", "repo", head="feature/Z")
    call = api._request.call_args
    params = call[1].get("params") or {}
    assert params.get("head") == "feature/Z"