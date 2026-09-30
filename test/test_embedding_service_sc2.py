"""Tests for embedding_service.Encode — SC-2 (Phase 2, Item 2).

Behavioral contract for the sentence-embedding encoder backed by the
byte-pinned gte-small model at models/gte-small/ (ONNX + tokenizer.json):

- encode(str) returns shape (1, 384) float32 array
- encoding a non-empty string yields a unit-norm vector (L2 == 1.0)
- encode(list_of_64_strings) pads the batch to (64, 384) float32
- invalid input (None, numbers, invalid element types) raises a
  contextual error (ValueError or subclass) naming the problem

The primary RED failure: src/services/embedding_service.py and its
encode() function do not exist yet, so every test fails with
ImportError/ModuleNotFoundError.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import pytest
import numpy as np


MODEL_DIR = "models/gte-small"
EXPECTED_DIM = 384


class TestEncodeContract:
    """SC-2 behavioral contract tests for embedding_service.encode."""

    def _encode(self, text):
        from src.services import embedding_service

        return embedding_service.encode(text)

    def test_encode_single_string_shape(self):
        vec = self._encode("kukukʉw")
        arr = np.asarray(vec)
        assert arr.shape == (1, EXPECTED_DIM)

    def test_encode_single_string_dtype_float32(self):
        vec = self._encode("hello world")
        assert np.asarray(vec).dtype == np.float32

    def test_encode_unit_norm(self):
        vec = self._encode("kuhkoohtu")
        arr = np.asarray(vec)
        norm = np.linalg.norm(arr.reshape(-1))
        assert norm == pytest.approx(1.0, abs=1e-5)

    def test_encode_batch_64_padding(self):
        texts = [f"record {i}" for i in range(64)]
        out = self._encode(texts)
        arr = np.asarray(out)
        assert arr.shape == (64, EXPECTED_DIM)
        assert arr.dtype == np.float32

    def test_encode_none_raises_contextual(self):
        with pytest.raises(ValueError) as excinfo:
            self._encode(None)
        msg = str(excinfo.value).lower()
        assert "input" in msg or "text" in msg or "type" in msg

    def test_encode_invalid_scalar_raises_contextual(self):
        with pytest.raises(ValueError):
            self._encode(12345)

    def test_encode_list_invalid_element_raises_contextual(self):
        with pytest.raises(ValueError):
            self._encode(["ok", None, [1, 2, 3]])