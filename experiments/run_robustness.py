# Robustness experiment: evaluate pipeline under paraphrase and synonym perturbations

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
from evaluation.robustness import QuestionPerturber


SAMPLE_SIZE = 20


def run_pipeline_fn(llm, loader):
    """Return a callable (question, db_id, evidence) -> sql."""
    schema_filter = SchemaFilter(llm)
    reasoner = ChainOfThoughtReasoner(llm)
    generator = SQLGenerator(llm)

    def pipeline_fn(question: str, db_id: str, evidence: str) -> str:
        full_schema = loader.get_schema(db_id)
        db_path = loader.get_db_path(db_id)
        filtered = schema_filter.filter(question, full_schema, evidence)
        reasoning = reasoner.reason(question, filtered, evidence)
        sql = generator.generate(question, filtered, evidence, reasoning)
        verifier = SQLVerifier(db_path, llm=llm)
        return verifier.get_final_sql(sql, verifier.verify(sql, filtered))

    return pipeline_fn


def main():
    loader = BirdLoader()
    examples = loader.load()[:SAMPLE_SIZE]
    llm = OpenAILLM()
    perturber = QuestionPerturber(llm)
    pipeline_fn = run_pipeline_fn(llm, loader)
    calculator = MetricsCalculator()

    original_correct = 0
    paraphrase_correct = 0
    synonym_correct = 0

    results = []

    for ex in tqdm(examples, desc="Robustness", ncols=70):
        db_path = loader.get_db_path(ex.db_id)
        executor = SQLExecutor(db_path)

        # Original
        orig_sql = pipeline_fn(ex.question, ex.db_id, ex.evidence)
        orig_correct = executor.compare(orig_sql, ex.gold_sql)
        if orig_correct:
            original_correct += 1

        # Paraphrase
        paraphrases = perturber.paraphrase(ex.question, n=1)
        para_q = paraphrases[0] if paraphrases else ex.question
        para_sql = pipeline_fn(para_q, ex.db_id, ex.evidence)
        para_correct = executor.compare(para_sql, ex.gold_sql)
        if para_correct:
            paraphrase_correct += 1

        # Synonym
        syn_q = perturber.synonym_replace(ex.question)
        syn_sql = pipeline_fn(syn_q, ex.db_id, ex.evidence)
        syn_correct = executor.compare(syn_sql, ex.gold_sql)
        if syn_correct:
            synonym_correct += 1

        results.append({
            "question_id": ex.question_id,
            "original_question": ex.question,
            "paraphrase": para_q,
            "synonym": syn_q,
            "original_correct": orig_correct,
            "paraphrase_correct": para_correct,
            "synonym_correct": syn_correct,
        })

    n = len(examples)
    summary = {
        "n": n,
        "ex_original": original_correct / n,
        "ex_paraphrase": paraphrase_correct / n,
        "ex_synonym": synonym_correct / n,
        "drop_paraphrase": (original_correct - paraphrase_correct) / n,
        "drop_synonym": (original_correct - synonym_correct) / n,
    }

    print("\n" + "=" * 50)
    print(f"Robustness Results (n={n}, GPT-4o-mini)")
    print("=" * 50)
    print(f"  Original:   {summary['ex_original']:.0%}")
    print(f"  Paraphrase: {summary['ex_paraphrase']:.0%}  (drop: {summary['drop_paraphrase']:.0%})")
    print(f"  Synonym:    {summary['ex_synonym']:.0%}  (drop: {summary['drop_synonym']:.0%})")
    print("=" * 50)

    output = {"summary": summary, "details": results}
    with open("results_robustness.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("\nSaved to results_robustness.json")


if __name__ == "__main__":
    main()
