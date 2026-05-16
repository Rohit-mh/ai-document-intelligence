"""
OpenAI-compatible Embedding Provider.

Uses the OpenAI embeddings API (or any compatible endpoint such as
GitHub Models at https://models.inference.ai.azure.com) to generate
embeddings for text — no local GPU/model download required.

Default model: text-embedding-3-small  (1 536-dim, very fast, cheap)
"""

import logging
import os
from typing import List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

GITHUB_BASE_URL = "https://models.inference.ai.azure.com"
DEFAULT_MODEL = "text-embedding-3-small"
# text-embedding-3-small produces 1 536-dimensional vectors
_ZERO_DIM = 1536


class OpenAIEmbeddingModel:
    """
    Embedding model that calls the OpenAI-compatible embeddings endpoint.

    Works with:
    - GitHub Models  (base_url = https://models.inference.ai.azure.com,
                      api_key  = GITHUB_TOKEN)
    - OpenAI proper  (base_url = https://api.openai.com/v1,
                      api_key  = OPENAI_API_KEY)
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = DEFAULT_MODEL,
        base_url: str = GITHUB_BASE_URL,
    ):
        if not api_key:
            raise ValueError(
                "GITHUB_TOKEN (or OPENAI_API_KEY) is required for OpenAI embeddings"
            )

        self.model_name = model_name
        self._dim: Optional[int] = None  # lazily resolved after first call

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        logger.info(
            f"OpenAI embedding model initialised: {model_name} @ {base_url}"
        )

    # ── helpers ──────────────────────────────────────────────────────────

    def _call(self, texts: List[str]) -> List[List[float]]:
        """Raw API call — returns list of float vectors."""
        # Strip empty strings to avoid API errors
        safe_texts = [t if t and t.strip() else " " for t in texts]
        response = self.client.embeddings.create(
            model=self.model_name,
            input=safe_texts,
        )
        # The API returns objects sorted by index
        vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
        if self._dim is None and vectors:
            self._dim = len(vectors[0])
        return vectors

    # ── public interface (same as LocalEmbeddingModel) ───────────────────

    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text string."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding — returning zero vector")
            return [0.0] * self.get_dimension()
        try:
            return self._call([text])[0]
        except Exception as e:
            logger.error(f"OpenAI embed() failed: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        try:
            # Split into chunks of 256 to stay within API limits
            results: List[List[float]] = []
            batch_size = 256
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                results.extend(self._call(batch))
            logger.info(f"OpenAI embed_batch: {len(results)} embeddings generated")
            return results
        except Exception as e:
            logger.error(f"OpenAI embed_batch() failed: {e}")
            raise

    def get_dimension(self) -> int:
        """Return the embedding dimension (resolved lazily)."""
        return self._dim or _ZERO_DIM


# ── singleton factory ─────────────────────────────────────────────────────

_openai_embedding_instance: Optional[OpenAIEmbeddingModel] = None


def get_openai_embedding_model(
    model_name: Optional[str] = None,
) -> OpenAIEmbeddingModel:
    """
    Get or create the OpenAI embedding model singleton.

    Reads from environment:
      GITHUB_TOKEN      — fine-grained PAT (also used for LLM)
      EMBEDDING_MODEL   — e.g. text-embedding-3-small (default)
    """
    global _openai_embedding_instance

    if _openai_embedding_instance is not None:
        return _openai_embedding_instance

    api_key = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY", "")
    model = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)
    base_url = os.getenv("EMBEDDING_BASE_URL", GITHUB_BASE_URL)

    _openai_embedding_instance = OpenAIEmbeddingModel(
        api_key=api_key,
        model_name=model,
        base_url=base_url,
    )
    return _openai_embedding_instance


def reset_openai_embedding_model() -> None:
    """Reset singleton (useful for tests)."""
    global _openai_embedding_instance
    _openai_embedding_instance = None
    logger.info("OpenAI embedding model instance reset")
