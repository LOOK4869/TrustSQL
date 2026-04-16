# Schema awareness: filter relevant tables and columns before SQL generation

import json
import re
from llms.base import BaseLLM


class SchemaFilter:
    """Filter a database schema to only the tables and columns relevant to a question."""

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm

    def filter(self, question: str, full_schema: dict[str, list[str]], evidence: str = "") -> dict[str, list[str]]:
        """
        Return a pruned schema containing only relevant tables and columns.

        Args:
            question: Natural language question.
            full_schema: Dict mapping table names to lists of column names.
            evidence: Optional domain knowledge hint from BIRD.

        Returns:
            Filtered schema dict. Falls back to full schema if parsing fails.
        """
        prompt = self._build_prompt(question, full_schema, evidence)
        response = self.llm.complete(prompt)
        filtered = self._parse_response(response, full_schema)
        # Safety: if filter returns empty, fall back to full schema
        if not filtered:
            return full_schema
        return filtered

    def _build_prompt(self, question: str, schema: dict[str, list[str]], evidence: str = "") -> str:
        """Build the LLM prompt for schema relevance filtering."""
        schema_lines = []
        for table, cols in schema.items():
            schema_lines.append(f"  {table}: {', '.join(cols)}")
        schema_str = "\n".join(schema_lines)

        prompt = f"""You are a database schema analyst. Given a question and a database schema, identify which tables and columns are needed to answer the question.

## Database Schema
{schema_str}
"""
        if evidence:
            prompt += f"\n## Evidence\n{evidence}\n"

        prompt += f"""
## Question
{question}

## Instructions
- Return ONLY a JSON object mapping table names to lists of relevant column names.
- Use the EXACT table and column names from the schema above — do not modify or abbreviate them.
- Be INCLUSIVE rather than exclusive: if a column might be needed for filtering, joining, or computing, include it.
- Always include primary key and foreign key columns for any table you include.
- When in doubt, include the column.

Example format:
```json
{{
  "table1": ["col1", "col2"],
  "table2": ["col3"]
}}
```

## Relevant Schema (JSON)
"""
        return prompt

    def _parse_response(self, response: str, full_schema: dict[str, list[str]]) -> dict[str, list[str]]:
        """Parse LLM response to extract the filtered schema."""
        # Try to extract JSON from ```json ... ``` block
        match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Try to find raw JSON object
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                return {}

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            return {}

        # Validate: keep only tables/columns that actually exist in full_schema
        filtered: dict[str, list[str]] = {}
        for table, cols in parsed.items():
            if table in full_schema:
                valid_cols = [c for c in cols if c in full_schema[table]]
                if valid_cols:
                    filtered[table] = valid_cols
                else:
                    # Table matched but no valid cols — include all cols of that table
                    filtered[table] = full_schema[table]

        return filtered
