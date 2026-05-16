"""Embedding models."""

from app.embeddings.local_embeddings import (
    get_embedding_model,
    reset_embedding_model,
)

__all__ = [
    "get_embedding_model",
    "reset_embedding_model",
]
