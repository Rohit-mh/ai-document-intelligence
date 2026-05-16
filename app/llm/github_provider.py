"""
GitHub Models LLM Provider Implementation.

Provides inference through the GitHub Models free endpoint
(https://models.inference.ai.azure.com) using the standard OpenAI SDK.
Requires a GitHub fine-grained personal access token (github_pat_…).
"""

import logging
import json
from typing import List, Dict, Any, Optional

from openai import OpenAI

from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

GITHUB_BASE_URL = "https://models.inference.ai.azure.com"


class GitHubProvider(BaseLLMProvider):
    """LLM provider that targets GitHub's free model inference endpoint."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o",
        temperature: float = 0.2,
    ):
        """
        Initialize GitHubProvider.

        Args:
            api_key: GitHub fine-grained personal access token (github_pat_…)
            model_name: Model to use (default: gpt-4o)
            temperature: Sampling temperature
        """
        super().__init__(model_name=model_name, temperature=temperature)

        if not api_key:
            raise ValueError("GITHUB_TOKEN not provided")

        self.client = OpenAI(
            base_url=GITHUB_BASE_URL,
            api_key=api_key,
        )
        logger.info(f"GitHub Models client initialized with model: {model_name}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs,
    ) -> str:
        """
        Generate text using the GitHub Models endpoint.

        Args:
            messages: List of message dicts (role/content)
            temperature: Optional temperature override
            max_tokens: Maximum tokens in the response
            **kwargs: Additional parameters forwarded to the API

        Returns:
            Generated text string
        """
        try:
            messages = self._prepare_messages(messages)
            temp = self._get_temperature(temperature)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=max_tokens,
                **kwargs,
            )

            result = response.choices[0].message.content or ""
            logger.debug(f"GitHub Models generation complete: {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"GitHub Models generation failed: {str(e)}")
            raise

    def generate_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a JSON response using the GitHub Models endpoint.

        Args:
            messages: List of message dicts
            temperature: Optional temperature override
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dictionary
        """
        try:
            messages_copy = list(messages)
            json_instruction = (
                "\n\nYou must respond with ONLY valid JSON, no markdown, no explanation."
            )
            if messages_copy and messages_copy[0].get("role") == "system":
                messages_copy[0] = dict(messages_copy[0])
                messages_copy[0]["content"] += json_instruction
            else:
                messages_copy.insert(
                    0,
                    {
                        "role": "system",
                        "content": "You must respond with ONLY valid JSON, no markdown, no explanation.",
                    },
                )

            text = self.generate(
                messages_copy,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Strip markdown code fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            result = json.loads(text)
            logger.debug(
                f"GitHub Models JSON generation complete: {len(json.dumps(result))} chars"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from GitHub Models: {str(e)}\nText: {text}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"GitHub Models JSON generation failed: {str(e)}")
            raise
