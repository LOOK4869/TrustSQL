# Baseline experiment: direct prompting with no schema filtering, reasoning, or verification

import argparse
from data.loader import BirdLoader
from llms.openai_llm import OpenAILLM
from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM
from evaluation.executor import SQLExecutor
from evaluation.metrics import MetricsCalculator, EvaluationRecord


def run_baseline(llm, examples, loader) -> list[EvaluationRecord]:
    """
    Run baseline evaluation: prompt the LLM directly without any pipeline components.

    Args:
        llm: LLM instance implementing BaseLLM.
        examples: List of BirdExample instances.
        loader: BirdLoader instance for schema and db path lookups.

    Returns:
        List of EvaluationRecord with predictions and correctness flags.
    """
    pass


def build_prompt(question: str, schema: dict[str, list[str]]) -> str:
    """
    Build a simple direct-prompting prompt without CoT or schema filtering.

    Args:
        question: Natural language question.
        schema: Full database schema dict.

    Returns:
        Prompt string to send to the LLM.
    """
    pass


def main() -> None:
    """Parse args, run baseline across all LLMs, print EX scores."""
    pass


if __name__ == "__main__":
    main()
