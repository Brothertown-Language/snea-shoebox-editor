"""ONNX-backed sentence embedding service for gte-small (SC-2, Issue #36).

Encodes text into unit-normalized float32 vectors of shape (N, 384) using
the byte-pinned quantized ONNX model and tokenizer under models/gte-small/.
Streamlit-import-free by design.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import threading
from pathlib import Path

import numpy as np

MODEL_PATH = Path("models/gte-small/onnx/model_qint8_avx512_vnni.onnx")
TOKENIZER_PATH = Path("models/gte-small/tokenizer.json")
MAX_LENGTH = 512
EXPECTED_DIM = 384
# Canonical pin for the embedding model. semantic_search_service re-exports
# this value; other modules should import from here.
PIN = "thenlper/gte-small"


class MissingModelAssetError(FileNotFoundError):
    """Raised when the pinned model or tokenizer bytes are absent."""


class InvalidTextInputError(ValueError):
    """Raised when input text is not str or a sequence of str."""


class _SessionHolder:
    """Module-level holder for the process-wide singleton InferenceSession."""

    def __init__(self):
        self._lock = threading.Lock()
        self._loader = None
        self._tokenizer = None
        self._session = None

    def get(self):
        return self._session

    def count(self):
        return 1 if self._session is not None else 0

    def set(self, loader, tokenizer, session):
        self._loader = loader
        self._tokenizer = tokenizer
        self._session = session

    def is_stale(self, loader):
        return self._session is None or self._loader is not loader


_SESSION_HOLDER = _SessionHolder()
_LOAD_LOCK = threading.Lock()
# Global encode lock: serializes every encode() caller end-to-end so
# concurrent Streamlit reruns (search query + backfill) never run ONNX
# inference in parallel — prevents RAM ballooning on constrained hosts.
_ENCODE_LOCK = threading.RLock()


def load_model():
    """Return the process-wide singleton InferenceSession.

    Exactly one onnxruntime.InferenceSession exists per process, held in
    _SESSION_HOLDER; concurrent callers share one in-flight load under
    _LOAD_LOCK so the model is constructed at most once. The holder is
    rebuilt only if the current _load_session differs from the one that
    produced the cached session.
    """
    with _LOAD_LOCK:
        if _SESSION_HOLDER.is_stale(_load_session):
            tokenizer, session = _load_session()
            _SESSION_HOLDER.set(_load_session, tokenizer, session)
        return _SESSION_HOLDER.get()


def _validate_input(text):
    if isinstance(text, str):
        return [text]
    if hasattr(text, "__iter__") and not isinstance(text, (bytes, bytearray)):
        items = list(text)
        for item in items:
            if not isinstance(item, str):
                raise InvalidTextInputError(
                    f"Invalid input: encode() accepts str or list of str; "
                    f"got list element of type {type(item).__name__!r}."
                )
        return items
    raise InvalidTextInputError(
        f"Invalid input: encode() accepts str or list of str; "
        f"got {type(text).__name__!r}."
    )


def _load_session():
    if not MODEL_PATH.is_file():
        raise MissingModelAssetError(f"Missing model bytes: {MODEL_PATH}")
    if not TOKENIZER_PATH.is_file():
        raise MissingModelAssetError(f"Missing tokenizer: {TOKENIZER_PATH}")
    import onnxruntime
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_file(str(TOKENIZER_PATH))
    tokenizer.enable_truncation(max_length=MAX_LENGTH)
    tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=None)
    options = onnxruntime.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = onnxruntime.InferenceSession(
        str(MODEL_PATH), sess_options=options, providers=["CPUExecutionProvider"]
    )
    return tokenizer, session


def encode(text):
    """Encode text (str or list of str) into float32 (N, 384) embeddings.

    Tokenizes with max length 512 + truncation, runs ONNX inference on the
    singleton session, mean-pools last_hidden_state over the attention
    mask, and L2-normalizes each vector.
    """
    if MODEL_PATH.is_file() is False:
        raise MissingModelAssetError(f"Missing model bytes: {MODEL_PATH}")

    texts = _validate_input(text)

    with _ENCODE_LOCK:
        load_model()
        tokenizer = _SESSION_HOLDER._tokenizer
        session = _SESSION_HOLDER.get()

        encodings = tokenizer.encode_batch(texts)
        input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)

        outputs = session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

    last_hidden = outputs[0].astype(np.float32)

    mask = attention_mask.astype(np.float32)[:, :, None]
    summed = (last_hidden * mask).sum(axis=1)
    counts = np.clip(mask.sum(axis=1), 1.0, None)
    pooled = summed / counts

    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return (pooled / norms).astype(np.float32)
