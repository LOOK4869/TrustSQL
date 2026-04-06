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
        """Return True if the query executed without error."""
        return self.error is None


class SQLExecutor:
    """Execute SQL queries against a sandboxed SQLite database."""

    def __init__(self, db_path: str) -> None:
        """
        Initialize with the path to the SQLite database file.

        Args:
            db_path: Filesystem path to the SQLite .sqlite file.
        """
        pass

    def execute(self, sql: str) -> ExecutionResult:
        """
        Execute a SQL query and return an ExecutionResult.

        Args:
            sql: SQL string to execute.

        Returns:
            ExecutionResult with rows or an error message.
        """
        pass

    def compare(self, sql_pred: str, sql_gold: str) -> bool:
        """
        Check whether predicted and gold SQL return identical result sets.

        Args:
            sql_pred: Generated SQL to evaluate.
            sql_gold: Ground-truth SQL from the BIRD benchmark.

        Returns:
            True if both queries produce the same rows (order-independent).
        """
        pass
