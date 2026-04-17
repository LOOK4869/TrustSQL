# Full pipeline experiment: schema filtering + CoT reasoning + SQL generation + verification

import argparse
import json
from tqdm import tqdm

from data.loader import BirdLoader
from llms.openai_llm import OpenAILLM
from llms.groq_llm import GroqLLM
from pipeline.schema_awareness import SchemaFilter
from pipeline.reasoning import ChainOfThoughtReasoner
from pipeline.sql_generator import SQLGenerator
from pipeline.verification import SQLVerifier
from evaluation.executor import SQLExecutor
from evaluation.metrics import EvaluationRecord, ErrorType, MetricsCalculator


def run_full_pipeline(llm, examples, loader, limit: int | None = None) -> list[EvaluationRecord]:
    """Run the complete TrustSQL pipeline on all examples."""
    schema_filter = SchemaFilter(llm)
    reasoner = ChainOfThoughtReasoner(llm)
    generator = SQLGenerator(llm)
    calculator = MetricsCalculator()
    records = []

    subset = examples[:limit] if limit else examples

    for ex in tqdm(subset, desc="Full Pipeline"):
        full_schema = loader.get_schema(ex.db_id)
        db_path = loader.get_db_path(ex.db_id)
        executor = SQLExecutor(db_path)

        # Step 1: Schema filtering
        filtered_schema = schema_filter.filter(ex.question, full_schema, ex.evidence)

        # Step 2: CoT reasoning
        reasoning = reasoner.reason(ex.question, filtered_schema, ex.evidence)

        # Step 3: SQL generation
        pred_sql = generator.generate(ex.question, filtered_schema, ex.evidence, reasoning)

        # Step 4: Verification + Self-correction
        verifier = SQLVerifier(db_path, llm=llm)
        verification = verifier.verify(pred_sql, filtered_schema)
        pred_sql = verifier.get_final_sql(pred_sql, verification)

        # Step 5: Evaluate
        exec_result = executor.execute(pred_sql)
        is_correct = executor.compare(pred_sql, ex.gold_sql)

        error_type = ErrorType.CORRECT if is_correct else calculator.classify_error(
            pred_sql, ex.gold_sql, full_schema,
            exec_error=exec_result.error,
        )

        records.append(EvaluationRecord(
            question_id=ex.question_id,
            db_id=ex.db_id,
            question=ex.question,
            sql_pred=pred_sql,
            sql_gold=ex.gold_sql,
            is_correct=is_correct,
            error_type=error_type,
            difficulty=ex.difficulty,
        ))

    return records


def main():
    parser = argparse.ArgumentParser(description="Run full pipeline experiment")
    parser.add_argument("--model", choices=["openai", "groq"], default="openai")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of examples")
    parser.add_argument("--output", type=str, default="results_full_pipeline.json")
    args = parser.parse_args()

    llm = OpenAILLM() if args.model == "openai" else GroqLLM()
    loader = BirdLoader()
    examples = loader.load()

    print(f"Running full pipeline with {args.model}, {args.limit or len(examples)} examples...")
    records = run_full_pipeline(llm, examples, loader, limit=args.limit)

    calculator = MetricsCalculator()
    summary = calculator.summarize(records)
    print(f"\n=== Full Pipeline Results ({args.model}) ===")
    print(summary)

    diff_breakdown = summary.by_difficulty(records)
    print("\nBy difficulty:")
    for diff, acc in sorted(diff_breakdown.items()):
        print(f"  {diff}: {acc:.1%}")

    output = {
        "model": args.model,
        "mode": "full_pipeline",
        "total": summary.total,
        "correct": summary.correct,
        "ex_accuracy": summary.execution_accuracy,
        "by_difficulty": {k: round(v, 4) for k, v in diff_breakdown.items()},
        "error_counts": summary.error_counts,
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
