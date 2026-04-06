# Entry point: run the full TrustSQL pipeline on a single natural language query

import argparse
from config import OPENAI_MODEL
from data.loader import BirdLoader
from pipeline.schema_awareness import SchemaFilter
from pipeline.reasoning import ChainOfThoughtReasoner
from pipeline.sql_generator import SQLGenerator
from pipeline.verification import SQLVerifier
from evaluation.executor import SQLExecutor
from llms.openai_llm import OpenAILLM


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run TrustSQL pipeline on a query.")
    parser.add_argument("--question", type=str, required=True, help="Natural language question")
    parser.add_argument("--db_id", type=str, required=True, help="BIRD database ID")
    parser.add_argument("--model", type=str, default=OPENAI_MODEL, help="LLM model name")
    return parser.parse_args()


def run_pipeline(question: str, db_id: str, llm) -> dict:
    """
    Run the full TrustSQL pipeline for a given question and database.

    Args:
        question: Natural language question to answer with SQL.
        db_id: BIRD benchmark database identifier.
        llm: An instantiated LLM object implementing BaseLLM.

    Returns:
        A dict with keys: filtered_schema, reasoning, sql, verification, result.
    """
    pass


def main() -> None:
    """Main entry point: parse args, run pipeline, print result."""
    pass


if __name__ == "__main__":
    main()
