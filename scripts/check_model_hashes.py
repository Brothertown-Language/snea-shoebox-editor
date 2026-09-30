#!/usr/bin/env python3
"""Issue #36 SC-1 - verify pinned gte-small model artifacts against SHA256 pins.

Exits non-zero on absent or byte-mismatched artifacts; prints digests.
The project root is resolved as the parent of the directory containing this
script (script lives at <root>/scripts/check_model_hashes.py).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PINS = {
    "models/gte-small/onnx/model_qint8_avx512_vnni.onnx": (
        "c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd",
    ),
    "models/gte-small/tokenizer.json": (
        "da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0",
    ),
}


def main() -> int:
    ok = True
    for rel, (sha_hex,) in PINS.items():
        path = PROJECT_ROOT / rel
        if not path.is_file():
            print(f"ABSENT: {rel}")
            ok = False
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{digest}  {rel}")
        if digest != sha_hex:
            print(f"  expected: {sha_hex}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())