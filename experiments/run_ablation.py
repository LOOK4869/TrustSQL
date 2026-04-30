# Ablation study: test each reliability mechanism individually vs combined

import json
from tqdm import tqdm

from data.loader import BirdLoader
from llms.openai_llm import OpenAILLM
from pipeline.schema_awareness import SchemaFilter
from pipeline.reasoning import ChainOfThoughtReasoner
from pipeline.sql_generator import SQLGenerator
from pipeline.verification import SQLVerifier
from evaluation.executor import SQLExecutor
from evaluation.metrics import MetricsCalculator, EvaluationRecord, ErrorType


def run_config(
    llm, examples, loader,
    use_schema: bool,
    use_cot: bool,
    use_verify: bool,
    label: str,
) -> dict:
    """Run a single ablation configuration and return summary stats."""
    schema_filter = SchemaFilter(llm) if use_schema else None
    reasoner = ChainOfThoughtReasoner(llm) if use_cot else None
    generator = SQLGenerator(llm)
    calculator = MetricsCalculator()
    records = []

    for ex in tqdm(examples, desc=label, ncols=70):
        full_schema = loader.get_schema(ex.db_id)
        db_path = loader.get_db_path(ex.db_id)
        executor = SQLExecutor(db_path)

        # Schema filtering
        schema = schema_filter.filter(ex.question, full_schema, ex.evidence) if use_schema else full_schema

        # CoT reasoning
        reasoning = reasoner.reason(ex.question, schema, ex.evidence) if use_cot else ""

        # SQL generation
        pred_sql = generator.generate(ex.question, schema, ex.evidence, reasoning)

        # Verification + Self-correction
        if use_verify:
            verifier = SQLVerifier(db_path, llm=llm)
            verification = verifier.verify(pred_sql, schema)
            pred_sql = verifier.get_final_sql(pred_sql, verification)

        # Evaluate
        exec_result = executor.execute(pred_sql)
        is_correct = executor.compare(pred_sql, ex.gold_sql)
        error_type = ErrorType.CORRECT if is_correct else calculator.classify_error(
            pred_sql, ex.gold_sql, full_schema, exec_error=exec_result.error
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

    summary = calculator.summarize(records)
    return {
        "label": label,
        "use_schema": use_schema,
        "use_cot": use_cot,
        "use_verify": use_verify,
        "correct": summary.correct,
        "total": summary.total,
        "ex_accuracy": summary.execution_accuracy,
        "error_counts": summary.error_counts,
    }


def main():
    loader = BirdLoader()
    examples = loader.load()[:20]
    llm = OpenAILLM()

    configs = [
        # (use_schema, use_cot, use_verify, label)
        (False, False, False, "Baseline (no mechanisms)"),
        (True,  False, False, "Schema only"),
        (False, True,  False, "CoT only"),
        (False, False, True,  "Verification only"),
        (True,  True,  True,  "Full Pipeline (all three)"),
    ]

    results = []
    for use_schema, use_cot, use_verify, label in configs:
        result = run_config(llm, examples, loader, use_schema, use_cot, use_verify, label)
        results.append(result)

    # Print comparison table
    print("\n" + "=" * 60)
    print(f"{'Configuration':<30} {'Correct':>8} {'EX Acc':>8}")
    print("=" * 60)
    baseline_ex = results[0]["ex_accuracy"]
    for r in results:
        delta = r["ex_accuracy"] - baseline_ex
        delta_str = f"({'+' if delta >= 0 else ''}{delta:.0%})" if delta != 0 else ""
        print(f"{r['label']:<30} {r['correct']:>4}/{r['total']:<4} {r['ex_accuracy']:>6.0%} {delta_str}")
    print("=" * 60)

    # Save
    with open("results_ablation.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved to results_ablation.json")


if __name__ == "__main__":
    main()
