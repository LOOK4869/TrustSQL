# LLM comparison experiment: run baseline and full pipeline across all available LLMs

import argparse
import json
from tqdm import tqdm

from data.loader import BirdLoader
from llms.openai_llm import OpenAILLM
from llms.groq_llm import GroqLLM
from experiments.run_baseline import run_baseline
from experiments.run_full_pipeline import run_full_pipeline
from evaluation.metrics import MetricsCalculator


def print_comparison_table(results: dict) -> None:
    """Print a formatted comparison table of EX scores across models and modes."""
    print("\n" + "=" * 65)
    print(f"{'Model':<20} {'Mode':<18} {'EX Accuracy':>12} {'Correct':>10}")
    print("=" * 65)
    for key, data in results.items():
        print(f"{data['model']:<20} {data['mode']:<18} {data['ex_accuracy']:>11.1%} {data['correct']:>5}/{data['total']}")
    print("=" * 65)

    # Show improvement per model
    print("\nPipeline improvement over baseline:")
    models = list({d["model"] for d in results.values()})
    for model in models:
        baseline_key = f"{model}_baseline"
        pipeline_key = f"{model}_full_pipeline"
        if baseline_key in results and pipeline_key in results:
            base_ex = results[baseline_key]["ex_accuracy"]
            pipe_ex = results[pipeline_key]["ex_accuracy"]
            delta = pipe_ex - base_ex
            print(f"  {model}: {base_ex:.1%} → {pipe_ex:.1%} ({'+' if delta >= 0 else ''}{delta:.1%})")


def main():
    parser = argparse.ArgumentParser(description="Compare LLMs on baseline and full pipeline")
    parser.add_argument("--limit", type=int, default=100, help="Number of examples per run")
    parser.add_argument("--output", type=str, default="results_comparison.json")
    args = parser.parse_args()

    loader = BirdLoader()
    examples = loader.load()
    calculator = MetricsCalculator()

    llms = {
        "gpt-4o-mini": OpenAILLM(),
        "llama-3.1-8b": GroqLLM(),
    }

    all_results = {}

    for model_name, llm in llms.items():
        print(f"\n{'='*50}")
        print(f"Model: {model_name}")
        print(f"{'='*50}")

        # Baseline
        print(f"\n[{model_name}] Running baseline...")
        baseline_records = run_baseline(llm, examples, loader, limit=args.limit)
        baseline_summary = calculator.summarize(baseline_records)
        key = f"{model_name}_baseline"
        all_results[key] = {
            "model": model_name,
            "mode": "baseline",
            "total": baseline_summary.total,
            "correct": baseline_summary.correct,
            "ex_accuracy": baseline_summary.execution_accuracy,
            "by_difficulty": baseline_summary.by_difficulty(baseline_records),
            "error_counts": baseline_summary.error_counts,
        }

        # Full pipeline
        print(f"\n[{model_name}] Running full pipeline...")
        pipeline_records = run_full_pipeline(llm, examples, loader, limit=args.limit)
        pipeline_summary = calculator.summarize(pipeline_records)
        key = f"{model_name}_full_pipeline"
        all_results[key] = {
            "model": model_name,
            "mode": "full_pipeline",
            "total": pipeline_summary.total,
            "correct": pipeline_summary.correct,
            "ex_accuracy": pipeline_summary.execution_accuracy,
            "by_difficulty": pipeline_summary.by_difficulty(pipeline_records),
            "error_counts": pipeline_summary.error_counts,
        }

    print_comparison_table(all_results)

    # Serialise (convert float keys in by_difficulty)
    serialisable = {}
    for k, v in all_results.items():
        v2 = dict(v)
        v2["by_difficulty"] = {dk: round(dv, 4) for dk, dv in v2["by_difficulty"].items()}
        serialisable[k] = v2

    with open(args.output, "w") as f:
        json.dump(serialisable, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
