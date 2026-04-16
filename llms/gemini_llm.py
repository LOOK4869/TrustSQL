# Google Gemini wrapper implementing the BaseLLM interface (uses google-genai SDK)

from google import genai
from google.genai import types
from llms.base import BaseLLM
from config import GOOGLE_API_KEY, GEMINI_MODEL, MAX_TOKENS, TEMPERATURE


class GeminiLLM(BaseLLM):
    """Gemini 2.0 Flash wrapper using the google-genai SDK."""

    def __init__(
        self,
        model: str = GEMINI_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        super().__init__(model, temperature, max_tokens)
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the completion text."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )
        return response.text.strip()

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat message list and return the model's response text."""
        # For simplicity, concatenate all messages into a single prompt
        parts = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role}: {msg['content']}")
        prompt = "\n".join(parts)
        return self.complete(prompt)
