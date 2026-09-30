# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Crash-remediation tests for the embedding encode path and backfill.

Production remediation (embed backfill crash on Streamlit Community Cloud):

- The encode path is globally serialized: a module-level lock in
  embedding_service serializes all concurrent encode() callers end-to-end
  so concurrent Streamlit reruns cannot run ONNX sessions in parallel.
- The ONNX InferenceSession is configured with SessionOptions limiting
  intra_op_num_threads to 1, capping thread workspace allocation on the
  ~1 vCPU / ~1 GB cloud container.
- backfill_embeddings defaults to batch_size=1 so RAM does not balloon
  from padding a 512-row batch up to 512 tokens.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import inspect
import threading
import time

import numpy as np


class TestEncodeGlobalLock:
    """All encode callers are serialized by a module-level lock."""

    def test_encode_serializes_concurrent_calls(self):
        from src.services import embedding_service

        embeds = []
        release = threading.Event()

        class BlockingSession:
            def run(self, *_a, **_k):
                # Record entry, hold until released, confirm no other
                # caller entered concurrently.
                embeds.append("enter")
                release.wait(5)
                embeds.append("exit")
                return [np.zeros((1, 1, embedding_service.EXPECTED_DIM), dtype=np.float32)]

        class BlockingTokenizer:
            def encode_batch(self, texts):
                return [type("E", (), {"ids": [0], "attention_mask": [1]})() for _ in texts]

        holder = embedding_service._SESSION_HOLDER
        holder.set(embedding_service._load_session, BlockingTokenizer(), BlockingSession())

        try:
            t1 = threading.Thread(target=lambda: embedding_service.encode("a"))
            t1.start()
            time.sleep(0.2)
            embedding_service.encode("b")
            release.set()
            t1.join(5)
            # No two "enter" events without an intervening "exit" — the
            # second caller must have waited for the first to finish.
            for prev, cur in zip(embeds, embeds[1:], strict=False):
                assert not (prev == "enter" and cur == "enter"), f"concurrent entry: {embeds}"
            assert embeds == ["enter", "exit", "enter", "exit"], f"unexpected sequence: {embeds}"
        finally:
            holder.set(None, None, None)

    def test_encode_lock_exists_and_is_used(self):
        from src.services import embedding_service

        assert hasattr(embedding_service, "_ENCODE_LOCK")
        src = inspect.getsource(embedding_service.encode)
        assert "_ENCODE_LOCK" in src


class TestSessionOptions:
    """ONNX session limits intra-op threads to 1."""

    def test_load_session_sets_intra_op_threads(self):
        from src.services import embedding_service

        src = inspect.getsource(embedding_service._load_session)
        assert "SessionOptions" in src
        assert "intra_op_num_threads" in src
        assert "inter_op_num_threads" in src
        assert "1" in src


class TestBackfillBatchSize:
    """backfill defaults to batch_size=1 (sequential, no RAM ballooning)."""

    def test_default_batch_size_is_one(self):
        from src.services.semantic_search_service import backfill_embeddings

        sig = inspect.signature(backfill_embeddings)
        assert sig.parameters["batch_size"].default == 1

    def test_backfill_encodes_row_at_a_time(self, monkeypatch):
        from src.services import semantic_search_service as sss

        calls = []
        monkeypatch.setattr(
            sss.embedding_service, "encode", lambda texts: calls.append(list(texts)) or np.zeros((len(texts), 1))
        )

        class Row:
            def __init__(self, id, term):
                self.id, self.term = id, term

        class Conn:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def execute(self, sql, params):
                # gloss table query returns 2 rows; semantic table query
                # returns 1 row → 3 stale rows total.
                if "gloss_search_entries" in str(sql):
                    return [Row(1, "t1"), Row(2, "t2")]
                return [Row(3, "t3")]

        class Engine:
            def connect(self):
                return Conn()

            def begin(self):
                return Conn()

        monkeypatch.setattr(sss, "_get_engine", lambda: Engine())

        result = sss.backfill_embeddings()
        assert result == {"total": 3, "backfilled": 3}
        assert calls == [["t1"], ["t2"], ["t3"]], f"expected one row per encode call, got {calls}"
