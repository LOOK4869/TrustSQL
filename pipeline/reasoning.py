# Reasoning: generate intermediate chain-of-thought steps to guide SQL construction

from llms.base import BaseLLM


class ChainOfThoughtReasoner:
    """Generate step-by-step reasoning for a natural language question before SQL generation."""

    def __init__(self, llm: BaseLLM) -> None:
        """
        Initialize with an LLM used for reasoning generation.

        Args:
            llm: LLM instance implementing BaseLLM.
        """
        pass

    def reason(self, question: str, filtered_schema: dict[str, list[str]]) -> str:
        """
        Produce a chain-of-thought reasoning string for the given question and schema.

        Args:
            question: Natural language question.
            filtered_schema: Pruned schema dict from SchemaFilter.

        Returns:
            Multi-step reasoning text to be included in the SQL generation prompt.
        """
        pass

    def _build_prompt(self, question: str, schema: dict[str, list[str]]) -> str:
        """Build the CoT reasoning prompt."""
        pass
