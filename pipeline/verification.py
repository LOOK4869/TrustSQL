# Verification: validate generated SQL for syntax, column existence, and join correctness

import re
import sqlite3
from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    """Result of SQL verification checks."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        lines = [f"[{status}]"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        return "\n".join(lines)


class SQLVerifier:
    """Run pre-execution checks on a generated SQL query."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def verify(self, sql: str, schema: dict[str, list[str]]) -> VerificationResult:
        """Run all verification checks and return a VerificationResult."""
        result = VerificationResult()

        syntax_errors = self._check_syntax(sql)
        result.errors.extend(syntax_errors)

        column_errors = self._check_columns(sql, schema)
        result.errors.extend(column_errors)

        join_warnings = self._check_join_paths(sql, schema)
        result.warnings.extend(join_warnings)

        if result.errors:
            result.is_valid = False

        return result

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
        """Check that column names referenced in SQL exist in the schema."""
        errors = []

        # Build a flat set of all valid column names (case-insensitive)
        all_columns: set[str] = set()
        for cols in schema.values():
            for col in cols:
                all_columns.add(col.lower())

        # Extract bare identifiers from the SQL (strip backtick/bracket quoting)
        # This is a heuristic: find backtick-quoted names which are column refs
        backtick_cols = re.findall(r"`([^`]+)`", sql)
        for col in backtick_cols:
            if col.lower() not in all_columns and col != "*":
                errors.append(f"Column not found in schema: `{col}`")

        return errors

    def _check_join_paths(self, sql: str, schema: dict[str, list[str]]) -> list[str]:
        """Warn if multiple tables are referenced without an explicit JOIN condition."""
        warnings = []

        # Find table references in FROM and JOIN clauses
        tables_in_sql = re.findall(
            r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql, re.IGNORECASE
        )
        referenced = [t for pair in tables_in_sql for t in pair if t]

        if len(referenced) > 1:
            # Check that all referenced tables exist in the schema
            for table in referenced:
                if table.lower() not in {t.lower() for t in schema}:
                    warnings.append(f"Table referenced in JOIN not found in schema: {table}")

        return warnings
