# Metrics: compute EX accuracy and categorize SQL error types

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
    OTHER = "other"


@dataclass
class EvaluationRecord:
    """A single evaluated example with prediction, gold, and outcome."""

    question: str
    db_id: str
    sql_pred: str
    sql_gold: str
    is_correct: bool
    error_type: ErrorType | None = None


@dataclass
class MetricsSummary:
    """Aggregated evaluation metrics over a set of examples."""

    total: int = 0
    correct: int = 0
    error_counts: dict[str, int] = field(default_factory=dict)

    @property
    def execution_accuracy(self) -> float:
        """Execution accuracy (EX): fraction of correct predictions."""
        return self.correct / self.total if self.total > 0 else 0.0


class MetricsCalculator:
    """Compute EX accuracy and error type distributions from evaluation records."""

    def compute_ex(self, records: list[EvaluationRecord]) -> float:
        """
        Compute execution accuracy over a list of EvaluationRecords.

        Args:
            records: List of evaluated examples.

        Returns:
            EX score as a float in [0, 1].
        """
        pass

    def summarize(self, records: list[EvaluationRecord]) -> MetricsSummary:
        """
        Produce a MetricsSummary with overall accuracy and per-error-type counts.

        Args:
            records: List of evaluated examples.

        Returns:
            MetricsSummary aggregating all records.
        """
        pass

    def classify_error(self, sql_pred: str, sql_gold: str, schema: dict[str, list[str]]) -> ErrorType:
        """
        Classify why a predicted SQL failed compared to gold SQL.

        Args:
            sql_pred: Predicted SQL string.
            sql_gold: Gold SQL string.
            schema: Database schema dict.

        Returns:
            The most likely ErrorType for this failure.
        """
        pass
