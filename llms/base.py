# Abstract base class defining the LLM interface used throughout the pipeline

from abc import ABC, abstractmethod
from config import MAX_TOKENS, TEMPERATURE


class BaseLLM(ABC):
    """Abstract interface for all LLM providers. All pipeline code must use this interface."""

    def __init__(self, model: str, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> None:
        """
        Initialize common LLM settings.

        Args:
            model: Model identifier string (e.g. 'gpt-4o-mini').
            temperature: Sampling temperature; 0.0 for deterministic output.
            max_tokens: Maximum number of tokens to generate.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        Send a prompt and return the model's text response.

        Args:
            prompt: The full prompt string to send to the LLM.

        Returns:
            The model's response as a plain string.
        """
        pass

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Send a list of chat messages and return the model's text response.

        Args:
            messages: List of dicts with 'role' and 'content' keys.

        Returns:
            The model's response as a plain string.
        """
        pass
