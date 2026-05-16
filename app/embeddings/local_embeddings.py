"""
Embedding model factory.

Routes to:
  - OpenAI / GitHub Models  (EMBEDDING_PROVIDER=openai, default)
  - Local sentence-transformers  (EMBEDDING_PROVIDER=local)

The public surface (get_embedding_model / reset_embedding_model) is unchanged
so all callers (chroma_manager, llm_client, runner) continue to work without
any modification.
"""

import logging
import os
from typing import Optional, Union

logger = logging.getLogger(__name__)

# Lazy singleton — holds whichever concrete model is active
_embedding_model = None


def get_embedding_model(model_name: Optional[str] = None):
    """
    Get or create the embedding model singleton.

    Reads EMBEDDING_PROVIDER from env:
      'openai'  → OpenAIEmbeddingModel via GitHub Models (default)
      'local'   → LocalEmbeddingModel via sentence-transformers

    Args:
        model_name: Optional model name override.

    Returns:
        An object with .embed(text) -> List[float]
                   and .embed_batch(texts) -> List[List[float]]
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

    if provider == "local":
        _embedding_model = _create_local(model_name)
    else:
        # default → openai-compatible (GitHub Models)
        _embedding_model = _create_openai(model_name)

    return _embedding_model


def reset_embedding_model() -> None:
    """Reset the singleton (useful for testing)."""
    global _embedding_model
    _embedding_model = None
    logger.info("Embedding model instance reset")


# ── private creators ──────────────────────────────────────────────────────

def _create_openai(model_name: Optional[str] = None):
    from app.embeddings.openai_embeddings import OpenAIEmbeddingModel
    import os

    api_key = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY", "")
    model = model_name or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    base_url = os.getenv(
        "EMBEDDING_BASE_URL", "https://models.inference.ai.azure.com"
    )
    logger.info(f"Creating OpenAI embedding model: {model}")
    return OpenAIEmbeddingModel(api_key=api_key, model_name=model, base_url=base_url)


def _create_local(model_name: Optional[str] = None):
    """Fall-back: local sentence-transformers model (no API key needed)."""
    import os
    from sentence_transformers import SentenceTransformer

    model = model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    logger.info(f"Creating local embedding model: {model}")
    return _LocalEmbeddingModel(model)


class _LocalEmbeddingModel:
    """Thin wrapper around SentenceTransformer with the same interface."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str):
        if not text or not text.strip():
            return [0.0] * self.get_dimension()
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()

    def embed_batch(self, texts):
        if not texts:
            return []
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
