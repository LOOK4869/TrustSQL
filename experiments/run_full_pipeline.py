# Full pipeline experiment: schema filtering + CoT reasoning + SQL generation + verification

import argparse
from data.loader import BirdLoader
from pipeline.schema_awareness import SchemaFilter
from pipeline.reasoning import ChainOfThoughtReasoner
from pipeline.sql_generator import SQLGenerator
from pipeline.verification import SQLVerifier
from evaluation.executor import SQLExecutor
from evaluation.metrics import MetricsCalculator, EvaluationRecord
from llms.openai_llm import OpenAILLM
from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM


def run_full_pipeline(llm, examples, loader) -> list[EvaluationRecord]:
    """
    Run the complete TrustSQL pipeline on all examples.

    Args:
        llm: LLM instance implementing BaseLLM.
        examples: List of BirdExample instances.
        loader: BirdLoader for schema and db path lookups.

    Returns:
        List of EvaluationRecord with predictions and correctness flags.
    """
    pass


def main() -> None:
    """Parse args, run full pipeline across all LLMs, print EX scores."""
    pass


if __name__ == "__main__":
    main()
