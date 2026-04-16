# Abstract base class defining the LLM interface used throughout the pipeline

from abc import ABC, abstractmethod
from config import MAX_TOKENS, TEMPERATURE


class BaseLLM(ABC):
    """Abstract interface for all LLM providers. All pipeline code must use this interface."""

    def __init__(self, model: str, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the model's text response."""
        pass

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a list of chat messages and return the model's text response."""
        pass
