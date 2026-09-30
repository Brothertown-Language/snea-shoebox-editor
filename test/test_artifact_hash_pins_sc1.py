"""Issue #36 SC-1 (structural) — artifact hash pin enforcement.

RED phase: the hash check must FAIL when models/gte-small/ artifacts are
absent or byte-mismatched against the recorded SHA256 pins.

Recorded pins (from .issues/36/plan-01-pinned-model-artifacts.md):
- ONNX   34,118,638 B  SHA256 c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd
- tokenizer.json 711,661 B  SHA256 da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HASH_SCRIPT = PROJECT_ROOT / "scripts" / "check_model_hashes.py"

RECORDED_PINS = {
    Path("models/gte-small/onnx/model_qint8_avx512_vnni.onnx"): (
        34118638,
        "c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd",
    ),
    Path("models/gte-small/tokenizer.json"): (
        711661,
        "da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0",
    ),
}


def _run_hash_check(cwd: Path | None = None, script_copy_root: Path | None = None):
    if script_copy_root is not None:
        # Fixture copy of the script inside a fake project root (negative path).
        fake_scripts = script_copy_root / "scripts"
        fake_scripts.mkdir(parents=True, exist_ok=True)
        fake_script = fake_scripts / HASH_SCRIPT.name
        if not fake_script.is_file():
            shutil.copy2(HASH_SCRIPT, fake_script)
        script = fake_script
    else:
        script = HASH_SCRIPT
    return subprocess.run(
        ["uv", "run", "python", str(script)],
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_sc1_artifacts_match_pins_and_hash_check_exit_zero():
    """SC-1 — committed artifacts must match recorded pins byte-for-byte and
    the hash check must exit 0 against them."""
    for rel, (size_b, sha256_hex) in RECORDED_PINS.items():
        path = PROJECT_ROOT / rel
        assert path.is_file(), f"missing artifact: {rel}"
        assert path.stat().st_size == size_b, (
            f"size drift for {rel}: {path.stat().st_size} != {size_b}"
        )
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == sha256_hex, f"sha256 mismatch for {rel}: {digest}"
    proc = _run_hash_check()
    assert proc.returncode == 0, (
        f"hash check failed against pins:\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    for rel, (_size, sha256_hex) in RECORDED_PINS.items():
        assert sha256_hex in proc.stdout, f"digest for {rel} not reported in stdout"


def test_sc1_hash_check_fails_on_byte_mismatch(tmp_path: Path):
    """Negative path — a byte-mismatched artifact must make the hash check
    exit non-zero. Exercises the script against a fake project root whose
    artifacts differ from the pins."""
    assert HASH_SCRIPT.is_file(), f"hash script missing: {HASH_SCRIPT}"
    fake_root = tmp_path / "fake-project"
    (fake_root).mkdir()
    for rel, (size_b, _sha) in RECORDED_PINS.items():
        src = PROJECT_ROOT / rel
        dst_root = fake_root
        assert src.is_file(), f"missing committed artifact: {rel}"
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = bytearray(src.read_bytes())
        # Corrupt: flip one byte (preserve size) for onnx; truncate for json.
        if dst.name.endswith(".json"):
            data = data[: size_b - 1]
        else:
            data[size_b // 2] ^= 0x01
        dst.write_bytes(bytes(data))
    proc = _run_hash_check(cwd=fake_root, script_copy_root=fake_root)
    assert proc.returncode != 0, (
        f"hash check exited 0 despite byte-mismatched artifacts:\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_sc1_hash_check_fails_on_absent_artifacts(tmp_path: Path):
    """Negative path — absent artifacts must make the hash check exit non-zero."""
    assert HASH_SCRIPT.is_file(), f"hash script missing: {HASH_SCRIPT}"
    fake_root = tmp_path / "empty-project"
    (fake_root / "models").mkdir(parents=True)
    proc = _run_hash_check(cwd=fake_root, script_copy_root=fake_root)
    assert proc.returncode != 0, "hash check exited 0 with artifacts absent"


@pytest.mark.parametrize(
    "rel,pins", [(str(k), v) for k, v in RECORDED_PINS.items()]
)
def test_sc1_pin_consistency_selfcheck(rel: str, pins):
    """Sanity: pin size and sha256 are mutually consistent against committed
    bytes (guards the pins themselves against transcription typos)."""
    path = PROJECT_ROOT / rel
    if not path.is_file():
        pytest.skip(f"artifact not committed yet (RED): {rel}")
    size_b, sha256_hex = pins
    assert path.stat().st_size == size_b
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha256_hex