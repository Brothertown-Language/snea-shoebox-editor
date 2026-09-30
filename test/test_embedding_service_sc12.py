"""Tests for embedding_service.load_model singleton — SC-12 (Phase 2, Item 12).

Behavioral contract: load_model() returns a process-wide single
onnxruntime.InferenceSession held in a module-level holder. Concurrent
load_model() calls are race-safe under an in-flight lock: the underlying
model construction happens at most once and every concurrent caller
receives the same session (registry count == 1). The module must remain
streamlit-import-free before and after load_model().

RED expectation: load_model() does not exist yet, so
AttributeError/ImportError paths fail.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""
import subprocess
import sys
import threading

from src.services import embedding_service


N_CALLERS = 8


def _install_counting_stub(monkeypatch):
    """Replace _load_session with a stub that counts constructions.

    The stub returns (tokenizer, session) sentinel objects so the test
    exercises the singleton/lock contract without loading real bytes.
    """
    state = {"count": 0, "session": object(), "tokenizer": object()}
    lock = threading.Lock()

    def stub():
        with lock:
            state["count"] += 1
        return state["tokenizer"], state["session"]

    monkeypatch.setattr(embedding_service, "_load_session", stub)
    return state


class TestLoadModelSingletonContract:
    """SC-12: process-wide single InferenceSession via load_model()."""

    def test_load_model_exists(self):
        assert hasattr(embedding_service, "load_model")

    def test_load_model_returns_session_twice_same_object(self, monkeypatch):
        state = _install_counting_stub(monkeypatch)
        s1 = embedding_service.load_model()
        s2 = embedding_service.load_model()
        assert s1 is s2
        assert state["count"] == 1

    def test_concurrent_load_model_single_construction(self, monkeypatch):
        state = _install_counting_stub(monkeypatch)
        results = []
        errors = []
        barrier = threading.Barrier(N_CALLERS)

        def worker():
            try:
                barrier.wait()
                results.append(embedding_service.load_model())
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(N_CALLERS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert len(results) == N_CALLERS
        first = results[0]
        assert all(r is first for r in results)
        assert state["count"] == 1

    def test_module_level_holder_registry_count(self, monkeypatch):
        state = _install_counting_stub(monkeypatch)
        session = embedding_service.load_model()
        holder = getattr(embedding_service, "_SESSION_HOLDER", None)
        assert holder is not None, (
            "load_model() must keep the singleton in a module-level holder"
        )
        count = getattr(holder, "count", None)
        if callable(count):
            count = count()
        assert count == 1
        assert holder.get() is session

    def test_streamlit_import_free(self):
        code = (
            "import sys\n"
            "from src.services import embedding_service\n"
            "embedding_service.load_model()\n"
            "assert 'streamlit' not in sys.modules, 'streamlit imported'\n"
            "print('OK')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.strip().endswith("OK")