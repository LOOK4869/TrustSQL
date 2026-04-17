# Reasoning: generate intermediate chain-of-thought steps to guide SQL construction

from llms.base import BaseLLM


class ChainOfThoughtReasoner:
    """Generate step-by-step reasoning for a natural language question before SQL generation."""

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm

    def reason(self, question: str, filtered_schema: dict[str, list[str]], evidence: str = "") -> str:
        """
        Produce a chain-of-thought reasoning string for the given question and schema.

        Args:
            question: Natural language question.
            filtered_schema: Pruned schema dict from SchemaFilter.
            evidence: Optional domain knowledge hint from BIRD.

        Returns:
            Multi-step reasoning text to be included in the SQL generation prompt.
        """
        prompt = self._build_prompt(question, filtered_schema, evidence)
        return self.llm.complete(prompt)

    def _build_prompt(self, question: str, schema: dict[str, list[str]], evidence: str = "") -> str:
        """Build the CoT reasoning prompt — focuses on logical structure only, not column names."""
        table_names = list(schema.keys())

        prompt = f"""You are a SQL query planner. Your job is to reason about the LOGICAL STRUCTURE of a SQL query — not to write SQL or name specific columns.

## Available Tables
{', '.join(table_names)}
"""
        if evidence:
            prompt += f"\n## Evidence\n{evidence}\n"

        prompt += f"""
## Question
{question}

## Instructions
Think through the following structural questions only. Do NOT mention specific column names — the SQL generator will handle that.

1. What type of result is needed? (a single value, a list, a count, etc.)
2. Which table(s) are likely involved?
3. Is a JOIN between tables needed? (yes/no, and why)
4. Is there a filtering condition? (yes/no, and what kind — equality, range, string match, etc.)
5. Is aggregation needed? (yes/no — COUNT, SUM, AVG, MAX, MIN)
6. Is sorting or row-limiting needed? (yes/no — ORDER BY, LIMIT)

Be concise. Answer each point in one sentence. Do not write any SQL.

## Logical Reasoning
"""
        return prompt
