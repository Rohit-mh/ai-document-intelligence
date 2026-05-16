"""
Groq LLM Provider Implementation.

Provides inference through the Groq API with fast reasoning capabilities.
"""

import logging
from typing import List, Dict, Any, Optional
import json

from groq import Groq

from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider using the Groq Python SDK."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
    ):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            model_name: Model to use (default: llama-3.1-8b-instant)
            temperature: Sampling temperature
        """
        super().__init__(model_name=model_name, temperature=temperature)
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not provided")
        
        self.client = Groq(api_key=api_key)
        logger.info(f"Groq client initialized with model: {model_name}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Generate text using Groq API.
        
        Args:
            messages: List of message dicts
            temperature: Optional temperature override
            max_tokens: Maximum tokens
            **kwargs: Additional parameters (top_p, frequency_penalty, etc.)
            
        Returns:
            Generated text
        """
        try:
            messages = self._prepare_messages(messages)
            temp = self._get_temperature(temperature)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=max_tokens,
                **kwargs
            )
            
            result = response.choices[0].message.content
            if result is None:
                result = ""
            logger.debug(f"Groq generation complete: {len(result)} chars")
            return result
            
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
            raise
    
    def generate_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Groq API.
        
        Args:
            messages: List of message dicts
            temperature: Optional temperature override
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Add JSON instruction to system message
            messages_copy = messages.copy()
            if messages_copy and messages_copy[0].get("role") == "system":
                messages_copy[0]["content"] += (
                    "\n\nYou must respond with ONLY valid JSON, no markdown, no explanation."
                )
            else:
                messages_copy.insert(
                    0,
                    {
                        "role": "system",
                        "content": "You must respond with ONLY valid JSON, no markdown, no explanation."
                    }
                )
            
            text = self.generate(
                messages_copy,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Parse JSON response
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            logger.debug(f"Groq JSON generation complete: {len(json.dumps(result))} chars")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq: {str(e)}\nText: {text}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Groq JSON generation failed: {str(e)}")
            raise
