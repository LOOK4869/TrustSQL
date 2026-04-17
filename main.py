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
from llms.groq_llm import GroqLLM


def get_llm(model_name: str):
    """Instantiate the correct LLM based on model name."""
    if "llama" in model_name.lower():
        return GroqLLM(model=model_name)
    return OpenAILLM(model=model_name)


def run_pipeline(question: str, db_id: str, llm, evidence: str = "", verbose: bool = False) -> dict:
    """
    Run the full TrustSQL pipeline for a given question and database.

    Args:
        question: Natural language question to answer with SQL.
        db_id: BIRD benchmark database identifier.
        llm: An instantiated LLM object implementing BaseLLM.
        evidence: Optional domain knowledge hint.
        verbose: Print intermediate steps if True.

    Returns:
        Dict with keys: filtered_schema, reasoning, sql, verification, result.
    """
    loader = BirdLoader()
    full_schema = loader.get_schema(db_id)
    db_path = loader.get_db_path(db_id)

    # Step 1: Schema Filtering
    schema_filter = SchemaFilter(llm)
    filtered_schema = schema_filter.filter(question, full_schema, evidence)
    if verbose:
        print("=== Step 1: Filtered Schema ===")
        for table, cols in filtered_schema.items():
            print(f"  {table}: {cols}")
        print()

    # Step 2: Chain-of-Thought Reasoning
    reasoner = ChainOfThoughtReasoner(llm)
    reasoning = reasoner.reason(question, filtered_schema, evidence)
    if verbose:
        print("=== Step 2: CoT Reasoning ===")
        print(reasoning)
        print()

    # Step 3: SQL Generation
    generator = SQLGenerator(llm)
    sql = generator.generate(question, filtered_schema, evidence, reasoning)
    if verbose:
        print("=== Step 3: Generated SQL ===")
        print(sql)
        print()

    # Step 4: Verification + Self-correction
    verifier = SQLVerifier(db_path, llm=llm)
    verification = verifier.verify(sql, filtered_schema)
    sql = verifier.get_final_sql(sql, verification)
    if verbose:
        print("=== Step 4: Verification ===")
        print(verification)
        if verification.corrected_sql:
            print(f"  Self-corrected SQL:\n  {verification.corrected_sql}")
        print()

    # Step 5: Execution
    executor = SQLExecutor(db_path)
    exec_result = executor.execute(sql)
    if verbose:
        print("=== Step 5: Execution Result ===")
        if exec_result.success:
            print(f"  Rows: {exec_result.rows}")
        else:
            print(f"  Error: {exec_result.error}")
        print()

    return {
        "filtered_schema": filtered_schema,
        "reasoning": reasoning,
        "sql": sql,
        "verification": verification,
        "result": exec_result,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run TrustSQL pipeline on a query.")
    parser.add_argument("--question", type=str, required=True, help="Natural language question")
    parser.add_argument("--db_id", type=str, required=True, help="BIRD database ID")
    parser.add_argument("--model", type=str, default=OPENAI_MODEL, help="LLM model name")
    parser.add_argument("--verbose", action="store_true", help="Print intermediate steps")
    return parser.parse_args()


def main() -> None:
    """Main entry point: parse args, run pipeline, print result."""
    args = parse_args()
    llm = get_llm(args.model)
    output = run_pipeline(args.question, args.db_id, llm, verbose=args.verbose)
    print("SQL:", output["sql"])
    result = output["result"]
    if result.success:
        print("Result:", result.rows)
    else:
        print("Execution Error:", result.error)


if __name__ == "__main__":
    main()
