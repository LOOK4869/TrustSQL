# Groq Llama 3 wrapper implementing the BaseLLM interface

import time
from groq import Groq, RateLimitError
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
        super().__init__(model, temperature, max_tokens)
        self.client = Groq(api_key=GROQ_API_KEY)

    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the completion text."""
        return self.chat([{"role": "user", "content": prompt}])

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat message list and return the assistant's response text. Retries on rate limit."""
        for attempt in range(5):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content.strip()
            except RateLimitError:
                wait = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                time.sleep(wait)
        raise RuntimeError("Groq rate limit exceeded after 5 retries")
