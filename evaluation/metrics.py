# Metrics: compute EX accuracy and categorize SQL error types

import re
from dataclasses import dataclass, field
from enum import Enum


class ErrorType(Enum):
    """Categories of SQL generation errors for failure analysis."""
    WRONG_TABLE = "wrong_table"
    WRONG_COLUMN = "wrong_column"
    WRONG_JOIN = "wrong_join"
    WRONG_CONDITION = "wrong_condition"
    SYNTAX_ERROR = "syntax_error"
    EXECUTION_ERROR = "execution_error"
    CORRECT = "correct"
    OTHER = "other"


@dataclass
class EvaluationRecord:
    """A single evaluated example with prediction, gold, and outcome."""
    question_id: int
    db_id: str
    question: str
    sql_pred: str
    sql_gold: str
    is_correct: bool
    error_type: ErrorType = ErrorType.OTHER
    difficulty: str = ""


@dataclass
class MetricsSummary:
    """Aggregated evaluation metrics over a set of examples."""
    total: int = 0
    correct: int = 0
    error_counts: dict[str, int] = field(default_factory=dict)

    @property
    def execution_accuracy(self) -> float:
        return self.correct / self.total if self.total > 0 else 0.0

    def by_difficulty(self, records: list["EvaluationRecord"]) -> dict[str, float]:
        """Return EX accuracy broken down by difficulty level."""
        groups: dict[str, list[bool]] = {}
        for r in records:
            groups.setdefault(r.difficulty, []).append(r.is_correct)
        return {
            diff: sum(results) / len(results)
            for diff, results in groups.items()
        }

    def __str__(self) -> str:
        lines = [
            f"EX Accuracy:  {self.correct}/{self.total} = {self.execution_accuracy:.1%}",
            "Error breakdown:",
        ]
        for err_type, count in sorted(self.error_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {err_type}: {count}")
        return "\n".join(lines)


class MetricsCalculator:
    """Compute EX accuracy and error type distributions from evaluation records."""

    def compute_ex(self, records: list[EvaluationRecord]) -> float:
        """Compute execution accuracy over a list of EvaluationRecords."""
        if not records:
            return 0.0
        return sum(r.is_correct for r in records) / len(records)

    def summarize(self, records: list[EvaluationRecord]) -> MetricsSummary:
        """Produce a MetricsSummary with overall accuracy and per-error-type counts."""
        summary = MetricsSummary(
            total=len(records),
            correct=sum(r.is_correct for r in records),
        )
        for r in records:
            key = r.error_type.value
            summary.error_counts[key] = summary.error_counts.get(key, 0) + 1
        return summary

    def classify_error(
        self,
        sql_pred: str,
        sql_gold: str,
        schema: dict[str, list[str]],
        exec_error: str | None = None,
    ) -> ErrorType:
        """
        Classify why a predicted SQL failed compared to gold SQL.

        Uses heuristics on the SQL strings and execution error message.
        """
        if exec_error:
            if "no such column" in exec_error.lower():
                return ErrorType.WRONG_COLUMN
            if "no such table" in exec_error.lower():
                return ErrorType.WRONG_TABLE
            if "syntax error" in exec_error.lower():
                return ErrorType.SYNTAX_ERROR
            return ErrorType.EXECUTION_ERROR

        # Extract tables mentioned in each SQL
        def extract_tables(sql: str) -> set[str]:
            return {
                t.lower()
                for pair in re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql, re.IGNORECASE)
                for t in pair if t
            }

        def extract_columns(sql: str) -> set[str]:
            return {c.lower() for c in re.findall(r"`([^`]+)`", sql)}

        tables_pred = extract_tables(sql_pred)
        tables_gold = extract_tables(sql_gold)
        cols_pred = extract_columns(sql_pred)
        cols_gold = extract_columns(sql_gold)

        if tables_pred != tables_gold:
            # Check if it's a join issue (same tables but different join structure)
            if "join" in sql_pred.lower() != ("join" in sql_gold.lower()):
                return ErrorType.WRONG_JOIN
            return ErrorType.WRONG_TABLE

        if cols_pred != cols_gold:
            return ErrorType.WRONG_COLUMN

        # Check WHERE conditions differ
        def extract_where(sql: str) -> str:
            m = re.search(r"\bWHERE\b(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)", sql, re.IGNORECASE | re.DOTALL)
            return m.group(1).strip().lower() if m else ""

        if extract_where(sql_pred) != extract_where(sql_gold):
            return ErrorType.WRONG_CONDITION

        return ErrorType.OTHER
