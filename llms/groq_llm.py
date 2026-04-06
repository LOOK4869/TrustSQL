# Groq Llama 3 wrapper implementing the BaseLLM interface

from groq import Groq
from llms.base import BaseLLM
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE


class GroqLLM(BaseLLM):
    """Llama 3 (via Groq) wrapper using the groq SDK."""

    def __init__(
        self,
        model: str = GROQ_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        """
        Initialize the Groq client.

        Args:
            model: Groq model identifier (e.g. 'llama3-8b-8192').
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
        """
        super().__init__(model, temperature, max_tokens)
        self.client = Groq(api_key=GROQ_API_KEY)

    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the completion text."""
        pass

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat message list and return the assistant's response text."""
        pass
