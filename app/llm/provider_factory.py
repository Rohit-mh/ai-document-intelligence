"""
Provider factory for creating LLM provider instances.

Supports GitHub Models (default) and Groq, with extensibility for future providers.
"""
import os

from dotenv import load_dotenv

load_dotenv()
import logging
import os
from typing import Optional



from app.llm.base import BaseLLMProvider
from app.llm.groq_provider import GroqProvider
from app.llm.github_provider import GitHubProvider

logger = logging.getLogger(__name__)

# Singleton instance
_provider_instance: Optional[BaseLLMProvider] = None


def get_llm_provider() -> BaseLLMProvider:
    """
    Get or create the LLM provider instance (singleton).

    Reads from environment variables:
    - LLM_PROVIDER: "github" (default) | "groq"
    - GITHUB_TOKEN: Required for GitHub Models
    - GITHUB_MODEL: Model name (default: gpt-4o)
    - GROQ_API_KEY: Required for Groq
    - GROQ_MODEL: Model name (default: llama-3.1-8b-instant)

    Returns:
        BaseLLMProvider instance

    Raises:
        ValueError: If configuration is invalid
    """
    global _provider_instance

    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("LLM_PROVIDER", "github").lower()

    if provider_name == "github":
        _provider_instance = _create_github_provider()
    elif provider_name == "groq":
        _provider_instance = _create_groq_provider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")

    return _provider_instance


def _create_github_provider() -> GitHubProvider:
    """Create GitHub Models provider instance."""
    api_key = os.getenv("GITHUB_TOKEN")
    if not api_key:
        raise ValueError(
            "GITHUB_TOKEN environment variable not set. "
            "Please provide your GitHub fine-grained token in .env file."
        )

    model = os.getenv("GITHUB_MODEL", "gpt-4o")
    temperature = float(os.getenv("GITHUB_TEMPERATURE", "0.2"))

    logger.info(f"Creating GitHub Models provider with model: {model}")
    return GitHubProvider(
        api_key=api_key,
        model_name=model,
        temperature=temperature,
    )


def _create_groq_provider() -> GroqProvider:
    """Create Groq provider instance (kept for backward compatibility)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable not set. "
            "Please provide your Groq API key in .env file."
        )

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    temperature = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

    logger.info(f"Creating Groq provider with model: {model}")
    return GroqProvider(
        api_key=api_key,
        model_name=model,
        temperature=temperature,
    )


def reset_provider() -> None:
    """Reset the provider instance (useful for testing)."""
    global _provider_instance
    _provider_instance = None
    logger.info("Provider instance reset")
