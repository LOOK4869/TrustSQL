# SQL generation: call LLM to produce SQL from filtered schema and CoT reasoning

from llms.base import BaseLLM


class SQLGenerator:
    """Generate SQL queries using an LLM given schema context and reasoning steps."""

    def __init__(self, llm: BaseLLM) -> None:
        """
        Initialize with an LLM used for SQL generation.

        Args:
            llm: LLM instance implementing BaseLLM.
        """
        pass

    def generate(self, question: str, filtered_schema: dict[str, list[str]], reasoning: str) -> str:
        """
        Generate a SQL query for the given question.

        Args:
            question: Natural language question.
            filtered_schema: Pruned schema from SchemaFilter.
            reasoning: Chain-of-thought reasoning text from ChainOfThoughtReasoner.

        Returns:
            Generated SQL string.
        """
        pass

    def _build_prompt(self, question: str, schema: dict[str, list[str]], reasoning: str) -> str:
        """Build the SQL generation prompt including schema and reasoning context."""
        pass

    def _extract_sql(self, response: str) -> str:
        """Extract the SQL statement from the raw LLM response."""
        pass
