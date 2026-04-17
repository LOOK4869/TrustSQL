# Verification: validate generated SQL and auto-correct errors via LLM self-correction

import re
import sqlite3
from dataclasses import dataclass, field
from llms.base import BaseLLM


@dataclass
class VerificationResult:
    """Result of SQL verification checks."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    corrected_sql: str | None = None  # Set if self-correction was applied

    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        lines = [f"[{status}]"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        if self.corrected_sql:
            lines.append(f"  CORRECTED SQL applied")
        return "\n".join(lines)


class SQLVerifier:
    """Run pre-execution checks on a generated SQL query, with optional self-correction."""

    def __init__(self, db_path: str, llm: BaseLLM | None = None) -> None:
        """
        Args:
            db_path: Path to the SQLite database file.
            llm: Optional LLM for self-correction. If None, only detection is performed.
        """
        self.db_path = db_path
        self.llm = llm

    def verify(self, sql: str, schema: dict[str, list[str]]) -> VerificationResult:
        """
        Run all verification checks. Self-correction is only triggered on confirmed
        SQLite syntax errors — column and join checks are advisory warnings only.

        Returns VerificationResult. If corrected, result.corrected_sql contains the fixed SQL.
        """
        result = VerificationResult()

        syntax_errors = self._check_syntax(sql)

        # Column and JOIN issues are reported as warnings, not hard errors.
        # They have high false-positive rates when schema is filtered, so we
        # do not use them to trigger self-correction.
        column_issues = self._check_columns(sql, schema)
        join_issues = self._check_join_paths(sql, schema)
        result.warnings.extend(column_issues)
        result.warnings.extend(join_issues)

        if syntax_errors:
            result.errors.extend(syntax_errors)
            result.is_valid = False
            # Only attempt self-correction for confirmed SQLite syntax errors
            if self.llm:
                corrected = self._self_correct(sql, schema, syntax_errors)
                if corrected and corrected != sql:
                    re_check = self._check_syntax(corrected)
                    if not re_check:
                        result.corrected_sql = corrected
                        result.is_valid = True

        return result

    def get_final_sql(self, original_sql: str, result: VerificationResult) -> str:
        """Return corrected SQL if available, otherwise the original."""
        return result.corrected_sql if result.corrected_sql else original_sql

    def _check_syntax(self, sql: str) -> list[str]:
        """Check SQL syntax by attempting EXPLAIN QUERY PLAN with SQLite."""
        errors = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(f"EXPLAIN QUERY PLAN {sql}")
            conn.close()
        except sqlite3.Error as e:
            errors.append(f"Syntax error: {e}")
        return errors

    def _check_columns(self, sql: str, schema: dict[str, list[str]]) -> list[str]:
        """Check that backtick-quoted column names in SQL exist in the schema."""
        errors = []
        all_columns: set[str] = {
            col.lower()
            for cols in schema.values()
            for col in cols
        }
        for col in re.findall(r"`([^`]+)`", sql):
            if col.lower() not in all_columns and col != "*":
                errors.append(f"Column not found in schema: `{col}`")
        return errors

    def _check_join_paths(self, sql: str, schema: dict[str, list[str]]) -> list[str]:
        """Warn if JOIN references a table not found in schema."""
        warnings = []
        tables_in_sql = re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql, re.IGNORECASE)
        referenced = [t for pair in tables_in_sql for t in pair if t]
        if len(referenced) > 1:
            for table in referenced:
                if table.lower() not in {t.lower() for t in schema}:
                    warnings.append(f"Table referenced in JOIN not found in schema: {table}")
        return warnings

    def _self_correct(self, sql: str, schema: dict[str, list[str]], errors: list[str]) -> str | None:
        """Ask the LLM to fix the SQL given the detected errors."""
        schema_lines = []
        for table, cols in schema.items():
            quoted_cols = [f"`{c}`" if (" " in c or "(" in c or "%" in c) else c for c in cols]
            schema_lines.append(f"  {table}({', '.join(quoted_cols)})")
        schema_str = "\n".join(schema_lines)

        error_str = "\n".join(f"- {e}" for e in errors)

        prompt = f"""The following SQLite SQL query has errors. Fix it using only the schema provided.

## Schema
{schema_str}

## Original SQL
{sql}

## Detected Errors
{error_str}

## Instructions
- Fix only the errors listed above.
- Use exact column and table names from the schema.
- Wrap column names containing spaces or special characters in backticks.
- Return only the fixed SQL wrapped in ```sql ... ``` block.

## Fixed SQL
"""
        try:
            response = self.llm.complete(prompt)
            # Extract SQL from response
            import re as _re
            match = _re.search(r"```sql\s*(.*?)\s*```", response, _re.DOTALL | _re.IGNORECASE)
            if match:
                return match.group(1).strip()
            match = _re.search(r"```\s*(.*?)\s*```", response, _re.DOTALL)
            if match:
                return match.group(1).strip()
            return response.strip()
        except Exception:
            return None
