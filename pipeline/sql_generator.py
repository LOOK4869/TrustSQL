# SQL generation: call LLM to produce SQL from schema context

import re
from llms.base import BaseLLM


class SQLGenerator:
    """Generate SQL queries using an LLM given schema context."""

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm

    def generate(
        self,
        question: str,
        schema: dict[str, list[str]],
        evidence: str = "",
        reasoning: str = "",
    ) -> str:
        """
        Generate a SQL query for the given question.

        Args:
            question: Natural language question.
            schema: Database schema dict {table: [columns]}.
            evidence: Domain knowledge hint from BIRD dataset.
            reasoning: Optional CoT reasoning text (used in Milestone 4+).

        Returns:
            Generated SQL string.
        """
        prompt = self._build_prompt(question, schema, evidence, reasoning)
        response = self.llm.complete(prompt)
        return self._extract_sql(response)

    def _build_prompt(
        self,
        question: str,
        schema: dict[str, list[str]],
        evidence: str,
        reasoning: str,
    ) -> str:
        """Build the SQL generation prompt."""
        # Wrap column names with spaces or special chars in backticks
        schema_lines = []
        for table, cols in schema.items():
            quoted_cols = [f"`{c}`" if (" " in c or "(" in c or "%" in c) else c for c in cols]
            schema_lines.append(f"  {table}({', '.join(quoted_cols)})")
        schema_str = "\n".join(schema_lines)

        prompt = f"""You are an expert SQLite SQL generator. Given a database schema and a question, write a valid SQLite SQL query.

## Database Schema
{schema_str}

## Critical Rules
- Use ONLY the exact table and column names listed in the schema above.
- Column names containing spaces or special characters are shown with backticks — use backticks when referencing them in SQL.
- Do NOT rename or simplify column names (e.g. do not turn `Free Meal Count (K-12)` into FreeMealCount).
- Write only SQLite-compatible SQL.
"""
        if evidence:
            prompt += f"\n## Evidence\n{evidence}\n"

        if reasoning:
            prompt += f"\n## Reasoning Steps\n{reasoning}\n"

        prompt += f"""
## Question
{question}

## Instructions
- Return only the SQL query wrapped in ```sql ... ``` code block.
- Do not explain, just return the SQL.

## SQL Query
"""
        return prompt

    def _extract_sql(self, response: str) -> str:
        """Extract the SQL statement from the raw LLM response."""
        # Try to find ```sql ... ``` block
        match = re.search(r"```sql\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback: find ``` ... ``` block
        match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Last resort: return the whole response stripped
        return response.strip()
