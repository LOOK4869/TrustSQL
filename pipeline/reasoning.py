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
        """Build the CoT reasoning prompt."""
        schema_lines = []
        for table, cols in schema.items():
            schema_lines.append(f"  {table}({', '.join(cols)})")
        schema_str = "\n".join(schema_lines)

        prompt = f"""You are a SQL reasoning assistant. Before writing SQL, think step by step about how to answer the question using the database schema.

## Database Schema
{schema_str}
"""
        if evidence:
            prompt += f"\n## Evidence\n{evidence}\n"

        prompt += f"""
## Question
{question}

## Instructions
Think through the following steps:
1. What information is being asked for? (SELECT target)
2. Which table(s) contain that information?
3. Are any JOINs needed? If so, on which keys?
4. Are there any WHERE conditions or filters?
5. Are aggregations (COUNT, SUM, AVG, MAX, MIN) or GROUP BY needed?
6. Is any ORDER BY or LIMIT needed?

Be concise. Use exact column names from the schema.

## Step-by-step Reasoning
"""
        return prompt
