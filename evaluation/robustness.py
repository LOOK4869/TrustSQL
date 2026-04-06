# Robustness testing: evaluate EX accuracy under semantic perturbations of questions

from llms.base import BaseLLM
from evaluation.metrics import EvaluationRecord


class QuestionPerturber:
    """Generate semantically equivalent paraphrases and synonym replacements of questions."""

    def __init__(self, llm: BaseLLM) -> None:
        """
        Initialize with an LLM used to generate paraphrases.

        Args:
            llm: LLM instance implementing BaseLLM.
        """
        pass

    def paraphrase(self, question: str, n: int = 3) -> list[str]:
        """
        Generate n paraphrased versions of the question.

        Args:
            question: Original natural language question.
            n: Number of paraphrases to generate.

        Returns:
            List of paraphrased question strings.
        """
        pass

    def synonym_replace(self, question: str) -> str:
        """
        Return a version of the question with key domain terms replaced by synonyms.

        Args:
            question: Original question string.

        Returns:
            Question with synonym substitutions applied.
        """
        pass


class RobustnessEvaluator:
    """Measure pipeline robustness by running evaluation on perturbed questions."""

    def __init__(self, perturber: QuestionPerturber) -> None:
        """
        Initialize with a QuestionPerturber.

        Args:
            perturber: Configured QuestionPerturber instance.
        """
        pass

    def evaluate(self, records: list[EvaluationRecord], pipeline_fn) -> dict[str, float]:
        """
        Run the pipeline on perturbed versions of each question and compute robustness scores.

        Args:
            records: Original evaluation records with ground-truth SQL.
            pipeline_fn: Callable (question, db_id) -> predicted SQL string.

        Returns:
            Dict with keys like 'ex_paraphrase' and 'ex_synonym' mapping to EX scores.
        """
        pass
