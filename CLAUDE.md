# TrustSQL — Project Context for Claude

## Project Overview
TrustSQL is a reliability-oriented Text-to-SQL research pipeline designed to improve the accuracy and robustness of LLM-generated SQL queries.

## Goal
Build and evaluate a three-component reliability pipeline:
1. **Schema Awareness** — Filter relevant tables and columns from large database schemas before prompting
2. **Knowledge & Reasoning** — Generate intermediate Chain-of-Thought reasoning steps to guide SQL construction
3. **Guardrails & Verification** — Post-generation checks for SQL validity, field existence, and join path correctness

## Dataset
- **BIRD Benchmark** (Big Bench for Large-scale Database Grounded Text-to-SQL Evaluation)
- Contains real-world, noisy databases with domain knowledge requirements

## LLMs Under Evaluation
| Model | Provider | API |
|-------|----------|-----|
| GPT-4o-mini | OpenAI | openai SDK |
| Gemini 1.5 Flash | Google | google-generativeai SDK |
| Llama 3 | Meta via Groq | groq SDK |

## Evaluation Metrics
- **EX (Execution Accuracy)** — Does the generated SQL produce the same result as gold SQL?
- **Robustness** — Does accuracy hold under semantic perturbations of the question?
- **Error Type Analysis** — Categorize failures: wrong table, wrong column, wrong join, wrong condition, etc.

## Pipeline Flow
```
User Question
    └─► Schema Filtering (schema_awareness.py)
            └─► Chain-of-Thought Reasoning (reasoning.py)
                    └─► SQL Generation (sql_generator.py)
                            └─► Verification (verification.py)
                                    └─► Execution & Scoring (executor.py + metrics.py)
```

## Repository Structure
```
trustsql/
├── config.py               # API keys, model configs, dataset paths
├── main.py                 # Full pipeline entry point
├── data/loader.py          # BIRD dataset loader
├── pipeline/               # Core pipeline components
├── llms/                   # LLM wrappers (OpenAI, Gemini, Groq)
├── evaluation/             # Execution, metrics, robustness testing
└── experiments/            # Experiment scripts for paper results
```

## Dev Notes
- All LLM calls go through the abstract `llms/base.py` interface — never call SDKs directly in pipeline code
- Use `.env` for all API keys, never hardcode
- SQL execution is always sandboxed against a local SQLite copy of BIRD databases
