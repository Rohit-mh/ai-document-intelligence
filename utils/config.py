"""
Configuration loader for the Document Intelligence System.
Loads environment variables from .env and provides centralized config access.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration manager for the Document Intelligence System."""

    # ── Provider Configuration ──
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "github")
    # GitHub Models (default provider)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_MODEL: str = os.getenv("GITHUB_MODEL", "gpt-4o")
    GITHUB_TEMPERATURE: float = float(os.getenv("GITHUB_TEMPERATURE", "0.2"))
    # Groq (kept for backward compatibility)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # ── ChromaDB Configuration ──
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "document_chunks")

    # ── Application Configuration ──
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # ── Supported File Types ──
    SUPPORTED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]

    @classmethod
    def validate(cls) -> list[str]:
        """Validate that all required environment variables are set.
        
        Returns:
            List of missing variable names. Empty list means all valid.
        """
        missing = []
        if cls.LLM_PROVIDER.lower() == "github" and not cls.GITHUB_TOKEN:
            missing.append("GITHUB_TOKEN")
        elif cls.LLM_PROVIDER.lower() == "groq" and not cls.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
            
        if cls.EMBEDDING_PROVIDER.lower() == "openai" and not cls.GITHUB_TOKEN:
            if "GITHUB_TOKEN" not in missing:
                missing.append("GITHUB_TOKEN")

        if missing:
            logger.warning(f"Missing environment variables: {', '.join(missing)}")
        else:
            logger.info("All required environment variables are set.")

        return missing

    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist."""
        Path(cls.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        Path("./data").mkdir(parents=True, exist_ok=True)
        logger.info("Required directories ensured.")

    @classmethod
    def get_summary(cls) -> dict:
        """Return a summary of the current configuration (without secrets)."""
        return {
            "llm_provider": cls.LLM_PROVIDER,
            "github_model": cls.GITHUB_MODEL,
            "groq_model": cls.GROQ_MODEL,
            "embedding_provider": cls.EMBEDDING_PROVIDER,
            "embedding_model": cls.EMBEDDING_MODEL,
            "chroma_dir": cls.CHROMA_PERSIST_DIR,
            "collection_name": cls.CHROMA_COLLECTION_NAME,
            "chunk_size": cls.MAX_CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "top_k": cls.TOP_K_RESULTS,
        }
