# LLM comparison experiment: run the same queries through GPT-4o-mini, Gemini, and Llama 3

import argparse
from data.loader import BirdLoader
from llms.openai_llm import OpenAILLM
from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM
from evaluation.metrics import MetricsCalculator, EvaluationRecord


def compare_llms(examples, loader) -> dict[str, list[EvaluationRecord]]:
    """
    Run the full pipeline with each LLM and return per-model evaluation records.

    Args:
        examples: List of BirdExample instances.
        loader: BirdLoader for schema and db path lookups.

    Returns:
        Dict mapping model name to list of EvaluationRecord.
    """
    pass


def print_comparison_table(results: dict[str, list[EvaluationRecord]]) -> None:
    """
    Print a formatted comparison table of EX scores across models.

    Args:
        results: Dict from compare_llms mapping model name to records.
    """
    pass


def main() -> None:
    """Parse args, run LLM comparison, print results table."""
    pass


if __name__ == "__main__":
    main()
