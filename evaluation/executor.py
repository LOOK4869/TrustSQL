# SQL executor: run generated and gold SQL against SQLite databases and return results

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionResult:
    """Result of executing a SQL query."""

    rows: list[tuple[Any, ...]]
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


class SQLExecutor:
    """Execute SQL queries against a sandboxed SQLite database."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def execute(self, sql: str) -> ExecutionResult:
        """Execute a SQL query and return an ExecutionResult."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = [tuple(row) for row in cursor.fetchall()]
            conn.close()
            return ExecutionResult(rows=rows)
        except Exception as e:
            return ExecutionResult(rows=[], error=str(e))

    def compare(self, sql_pred: str, sql_gold: str) -> bool:
        """
        Check whether predicted and gold SQL return identical result sets.

        Comparison is order-independent (sorted set comparison).
        """
        result_pred = self.execute(sql_pred)
        result_gold = self.execute(sql_gold)

        if not result_pred.success or not result_gold.success:
            return False

        # Normalise: sort rows for order-independent comparison
        def normalise(rows: list[tuple]) -> list[tuple]:
            return sorted([tuple(str(v) for v in row) for row in rows])

        return normalise(result_pred.rows) == normalise(result_gold.rows)
