"""
Centralized LLM initialization utility wrapper.
Redirects old calls to the new provider factory and local embeddings.
Includes token limiting and rate limit handling.
"""

import os
import json
import logging
import time
from dotenv import load_dotenv

from utils.config import Config
from app.llm.provider_factory import get_llm_provider
from app.embeddings.local_embeddings import get_embedding_model

load_dotenv()

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Token Estimation & Rate Limiting
# ──────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """
    Rough estimate of tokens in text.
    ~1 token per 4 characters is a reasonable estimate.
    """
    return len(text) // 4 + 10  # +10 for safety margin


def truncate_for_llm(text: str, max_chars: int = 24000) -> str:
    """
    Truncate text to fit within LLM context limits.

    Default: ~24000 chars ≈ 6000 tokens (fits within GitHub Models free tier limits).
    """
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    # Try to truncate at a sentence boundary
    last_period = truncated.rfind(".")
    if last_period > max_chars * 0.8:  # If period is reasonably close
        truncated = truncated[:last_period + 1]

    truncated += "\n\n[... document truncated due to length ...]"
    return truncated


# Keep the old name as an alias so existing callers don't break
truncate_for_groq = truncate_for_llm


# ──────────────────────────────────────────────
# Reusable LLM Call Functions
# ──────────────────────────────────────────────

def call_llm(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = 0.2,
    max_tokens: int = 4000,
    max_retries: int = 3,
) -> str:
    """
    Send a chat completion request using the new LLM Provider.
    Includes retry logic for rate limit errors.
    
    Args:
        user_prompt: The user's message/query.
        system_prompt: System instruction for the model.
        temperature: Controls randomness (0 = deterministic).
        max_tokens: Maximum output tokens.
        max_retries: Number of retries on rate limit error.
    
    Returns:
        The model's response text.
    
    Raises:
        Exception: If all retries fail or other error occurs.
    """
    llm = get_llm_provider()
    
    # Estimate tokens and warn if too large
    total_estimated_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt) + max_tokens
    if total_estimated_tokens > 5500:
        logger.warning(
            f"Estimated tokens ({total_estimated_tokens}) is large. "
            f"Consider using shorter inputs."
        )

    for attempt in range(max_retries):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            result = llm.generate(messages=messages, temperature=temperature, max_tokens=max_tokens)
            logger.info(f"LLM call successful. Response length: {len(result)} chars")
            return result
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit error
            if "rate_limit_exceeded" in error_msg or "413" in error_msg or "too large" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Rate limit error (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s. Error: {error_msg[:100]}"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    # All retries exhausted
                    raise RuntimeError(
                        f"LLM API rate limit or free tier limit exceeded. "
                        f"Estimated tokens: {total_estimated_tokens}. "
                        f"Please reduce the document size or try again in a minute."
                    )
            else:
                # Other error, don't retry
                logger.error(f"LLM chat call failed: {e}")
                raise
    
    # This shouldn't be reached
    raise RuntimeError("LLM call failed after all retries")


def call_llm_json(
    user_prompt: str,
    system_prompt: str,
    temperature: float = 0,
    max_retries: int = 3,
) -> dict:
    """
    Send a chat completion request expecting JSON output via the new provider.
    Includes retry logic for rate limit errors.
    
    Args:
        user_prompt: The user's message/query.
        system_prompt: System instruction that guides JSON extraction.
        temperature: Controls randomness (default 0 for structured output).
        max_retries: Number of retries on rate limit error.
    
    Returns:
        Parsed JSON dictionary.
    
    Raises:
        Exception: If all retries fail or JSON parsing fails.
    """
    llm = get_llm_provider()
    
    # Estimate tokens
    total_estimated_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt) + 2000
    if total_estimated_tokens > 5500:
        logger.warning(
            f"Estimated tokens ({total_estimated_tokens}) is large. "
            f"Consider using shorter inputs."
        )

    for attempt in range(max_retries):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            parsed = llm.generate_json(messages=messages, temperature=temperature)
            logger.info("LLM JSON call successful.")
            return parsed
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit error
            if "rate_limit_exceeded" in error_msg or "413" in error_msg or "too large" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Rate limit error on JSON call (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time}s."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(
                        f"LLM API rate limit or free tier limit exceeded on JSON request. "
                        f"Your request is too large for the free tier. Please try again in a minute."
                    )
            else:
                # Other error, don't retry
                logger.error(f"LLM JSON call failed: {e}")
                raise
    
    raise RuntimeError("LLM JSON call failed after all retries")


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings using local embeddings.
    
    Args:
        texts: List of text strings to embed.
    
    Returns:
        List of embedding vectors.
    """
    embedder = get_embedding_model()

    try:
        embeddings = embedder.embed_batch(texts)
        logger.info(f"Generated {len(embeddings)} embeddings.")
        return embeddings
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise
