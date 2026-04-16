# Robustness testing: evaluate EX accuracy under semantic perturbations of questions

import re
from llms.base import BaseLLM
from evaluation.metrics import EvaluationRecord, MetricsCalculator


class QuestionPerturber:
    """Generate semantically equivalent paraphrases of questions using an LLM."""

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm

    def paraphrase(self, question: str, n: int = 3) -> list[str]:
        """
        Generate n paraphrased versions of the question.

        Args:
            question: Original natural language question.
            n: Number of paraphrases to generate.

        Returns:
            List of paraphrased question strings.
        """
        prompt = f"""Generate {n} different paraphrases of the following question.
Keep the same meaning but use different wording.
Return each paraphrase on a new line, numbered 1. 2. 3. etc.

Question: {question}

Paraphrases:"""
        response = self.llm.complete(prompt)
        lines = response.strip().split("\n")
        paraphrases = []
        for line in lines:
            # Strip leading number and punctuation
            cleaned = re.sub(r"^\d+[\.\)]\s*", "", line.strip())
            if cleaned and cleaned.lower() != question.lower():
                paraphrases.append(cleaned)
        return paraphrases[:n]

    def synonym_replace(self, question: str) -> str:
        """
        Return a version of the question with key terms replaced by synonyms.

        Args:
            question: Original question string.

        Returns:
            Question with synonym substitutions applied.
        """
        prompt = f"""Rewrite the following question by replacing some key words with synonyms or alternative phrasings, while keeping the same meaning.

Original: {question}

Rewritten:"""
        response = self.llm.complete(prompt)
        # Take only the first line of the response
        return response.strip().split("\n")[0].strip()


class RobustnessEvaluator:
    """Measure pipeline robustness by running evaluation on perturbed questions."""

    def __init__(self, perturber: QuestionPerturber) -> None:
        self.perturber = perturber
        self.calculator = MetricsCalculator()

    def evaluate(
        self,
        records: list[EvaluationRecord],
        pipeline_fn,
        sample_size: int = 50,
    ) -> dict[str, float]:
        """
        Run the pipeline on perturbed versions of each question and compute robustness scores.

        Args:
            records: Original evaluation records with ground-truth SQL.
            pipeline_fn: Callable (question, db_id, evidence) -> predicted SQL string.
            sample_size: Number of records to sample for robustness testing.

        Returns:
            Dict with keys: 'ex_original', 'ex_paraphrase', 'ex_synonym', 'robustness_drop'.
        """
        sampled = records[:sample_size]
        calculator = MetricsCalculator()

        original_correct = sum(r.is_correct for r in sampled)

        paraphrase_correct = 0
        synonym_correct = 0

        for record in sampled:
            from evaluation.executor import SQLExecutor
            executor = SQLExecutor(self._get_db_path(record.db_id))

            # Test paraphrase robustness
            paraphrases = self.perturber.paraphrase(record.question, n=1)
            if paraphrases:
                para_sql = pipeline_fn(paraphrases[0], record.db_id, "")
                if executor.compare(para_sql, record.sql_gold):
                    paraphrase_correct += 1

            # Test synonym robustness
            synonym_q = self.perturber.synonym_replace(record.question)
            syn_sql = pipeline_fn(synonym_q, record.db_id, "")
            if executor.compare(syn_sql, record.sql_gold):
                synonym_correct += 1

        n = len(sampled)
        ex_original = original_correct / n
        ex_paraphrase = paraphrase_correct / n
        ex_synonym = synonym_correct / n

        return {
            "ex_original": ex_original,
            "ex_paraphrase": ex_paraphrase,
            "ex_synonym": ex_synonym,
            "robustness_drop_paraphrase": ex_original - ex_paraphrase,
            "robustness_drop_synonym": ex_original - ex_synonym,
        }

    def _get_db_path(self, db_id: str) -> str:
        from data.loader import BirdLoader
        return BirdLoader().get_db_path(db_id)
