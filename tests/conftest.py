"""
Test defaults: avoid loading sentence-transformers / torch for every test (memory-heavy on Windows).
Uses a fixed 384-dim stub compatible with bge-small-en-v1.5 vector size.
"""

import pytest

from app.embeddings import local_embeddings as le
import utils.chroma_manager as cm
import app.runner as runner_mod


class _StubEmbeddingModel:
    """Minimal embedder matching typical bge-small dimension (384)."""

    _dim = 384

    def embed(self, text: str) -> list[float]:
        if not text or not str(text).strip():
            return [0.0] * self._dim
        return [0.01] * self._dim

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


@pytest.fixture(autouse=True)
def _stub_heavy_ml_stack(monkeypatch):
    le.reset_embedding_model()
    cm._chroma_manager_instance = None
    runner_mod._runner_instance = None
    stub = _StubEmbeddingModel()
    # chroma_manager imported get_embedding_model by name at module load — patch that binding too
    monkeypatch.setattr(le, "get_embedding_model", lambda model_name=None: stub)
    monkeypatch.setattr(cm, "get_embedding_model", lambda model_name=None: stub)
    yield
    le.reset_embedding_model()
    cm._chroma_manager_instance = None
    runner_mod._runner_instance = None
