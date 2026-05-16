"""
Abstract base class for LLM providers.

Provides a unified interface for different LLM backends (Groq, OpenAI, Ollama, etc.)
allowing easy swapping without changing agent code.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Message(dict):
    """Message format compatible with OpenAI, Groq, and other providers."""
    
    def __init__(self, role: str, content: str):
        super().__init__(role=role, content=content)
    
    @property
    def role(self) -> str:
        return self.get("role")
    
    @property
    def content(self) -> str:
        return self.get("content")


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str, temperature: float = 0.2):
        """
        Initialize the LLM provider.
        
        Args:
            model_name: Name/ID of the model to use
            temperature: Sampling temperature (0-1)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.provider_name = self.__class__.__name__
        logger.info(f"{self.provider_name} initialized with model: {model_name}")
    
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs
    ) -> str:
        """
        Generate text based on messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Optional temperature override
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific arguments
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        pass
    
    @abstractmethod
    def generate_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            messages: List of message dicts
            temperature: Optional temperature override
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific arguments
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            Exception: If API call or JSON parsing fails
        """
        pass
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Prepare/validate messages before sending."""
        if not messages:
            raise ValueError("Messages cannot be empty")
        
        # Ensure all messages have role and content
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"Invalid message format: {msg}")
        
        return messages
    
    def _get_temperature(self, temperature: Optional[float]) -> float:
        """Get effective temperature value."""
        return temperature if temperature is not None else self.temperature
