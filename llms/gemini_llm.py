# Google Gemini 1.5 Flash wrapper implementing the BaseLLM interface

import google.generativeai as genai
from llms.base import BaseLLM
from config import GOOGLE_API_KEY, GEMINI_MODEL, MAX_TOKENS, TEMPERATURE


class GeminiLLM(BaseLLM):
    """Gemini 1.5 Flash wrapper using the google-generativeai SDK."""

    def __init__(
        self,
        model: str = GEMINI_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        """
        Initialize the Gemini client.

        Args:
            model: Gemini model identifier.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
        """
        super().__init__(model, temperature, max_tokens)
        genai.configure(api_key=GOOGLE_API_KEY)
        self.client = genai.GenerativeModel(model)

    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the completion text."""
        pass

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat message list and return the model's response text."""
        pass
