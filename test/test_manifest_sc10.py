"""SC-10 (Issue 36) structural manifest contract test.

Asserts runtime dependency manifest shape: onnxruntime + tokenizers in
[project] dependencies, sentence-transformers dev-only, and a profiler
evidence artifact with measured RSS below the 1 GiB envelope.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
PROFILER_DIR = PROJECT_ROOT / "tmp" / "issue-36" / "artifacts"
ENVELOPE_BYTES = 1024**3
MIB_TO_BYTES = 1024 * 1024


def _parse_pyproject() -> dict:
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)


def _get_dep_field(data: dict, table: str, field: str = "dependencies") -> list[str]:
    return list(data.get(table, {}).get(field, []))


def _dep_roots(deps: list[str]) -> set[str]:
    # Normalized (PEP 503) root package names
    def norm(name: str) -> str:
        root = name.split(";", 1)[0].split(">=", 1)[0].split("==", 1)[0].split("<", 1)[0]
        return root.strip().lower().replace("_", "-").replace(".", "-")

    return {norm(d) for d in deps}


def test_runtime_deps_contain_onnxruntime_and_tokenizers():
    data = _parse_pyproject()
    runtime = _dep_roots(_get_dep_field(data, "project"))
    assert "onnxruntime" in runtime, "onnxruntime missing from [project] dependencies"
    assert "tokenizers" in runtime, "tokenizers missing from [project] dependencies"


def test_sentence_transformers_absent_from_runtime_deps():
    data = _parse_pyproject()
    runtime = _dep_roots(_get_dep_field(data, "project"))
    assert "sentence-transformers" not in runtime, (
        "sentence-transformers must NOT be a runtime dependency"
    )


def test_sentence_transformers_present_in_dev_group():
    data = _parse_pyproject()
    dev = _dep_roots(list(data.get("dependency-groups", {}).get("dev", [])))
    assert "sentence-transformers" in dev, "sentence-transformers missing from dev group"


def test_profiler_evidence_artifact_exists_and_within_envelope():
    artifacts = sorted(PROFILER_DIR.glob("profiler-sc12-resident-set-*.yaml"))
    assert artifacts, "no profiler-sc12-resident-set-*.yaml evidence artifact found"
    assert any(
        p.name == "profiler-sc12-resident-set-20260929195251.yaml" for p in artifacts
    ), "expected profiler artifact profiler-sc12-resident-set-20260929195251.yaml missing"
    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8")
        assert "resident_set_after_mib" in text, f"{artifact.name}: missing RSS field"
        rss_mib = float(
            text.split("resident_set_after_mib:", 1)[1]
            .split("\n", 1)[0]
            .strip()
            .split()[0]
        )
        assert rss_mib * MIB_TO_BYTES < ENVELOPE_BYTES, (
            f"{artifact.name}: measured RSS {rss_mib} MiB exceeds 1 GiB envelope"
        )