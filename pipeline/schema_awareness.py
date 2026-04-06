# Schema awareness: filter relevant tables and columns before SQL generation

from typing import Any
from llms.base import BaseLLM
from config import MAX_SCHEMA_TABLES


class SchemaFilter:
    """Filter a database schema to only the tables and columns relevant to a question."""

    def __init__(self, llm: BaseLLM) -> None:
        """
        Initialize with an LLM used to assess relevance.

        Args:
            llm: LLM instance implementing BaseLLM.
        """
        pass

    def filter(self, question: str, full_schema: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Return a pruned schema containing only relevant tables and columns.

        Args:
            question: Natural language question.
            full_schema: Dict mapping table names to lists of column names.

        Returns:
            Filtered schema dict with the same structure.
        """
        pass

    def _build_prompt(self, question: str, schema: dict[str, list[str]]) -> str:
        """Build the LLM prompt for schema relevance filtering."""
        pass

    def _parse_response(self, response: str, full_schema: dict[str, list[str]]) -> dict[str, list[str]]:
        """Parse LLM response to extract the filtered schema."""
        pass
