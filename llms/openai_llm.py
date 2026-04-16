# OpenAI GPT-4o-mini wrapper implementing the BaseLLM interface

import openai
from llms.base import BaseLLM
from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS, TEMPERATURE


class OpenAILLM(BaseLLM):
    """GPT-4o-mini wrapper using the openai SDK."""

    def __init__(
        self,
        model: str = OPENAI_MODEL,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        super().__init__(model, temperature, max_tokens)
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the completion text."""
        return self.chat([{"role": "user", "content": prompt}])

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Send a chat message list and return the assistant's response text."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content.strip()
