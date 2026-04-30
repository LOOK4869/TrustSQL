# TrustSQL: A Reliability-Oriented Text-to-SQL Pipeline

TrustSQL improves the reliability of LLM-generated SQL on real-world databases through a three-stage pipeline evaluated on the BIRD benchmark.

---

## Pipeline

```
User Question
     │
     ▼
┌─────────────────────┐
│  Schema Awareness   │  Filter relevant tables & columns from full schema
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  CoT Reasoning      │  Plan query logic (JOIN, aggregation, sorting)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  SQL Generation     │  LLM generates SQL from filtered schema + reasoning
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Verification       │  Syntax check + LLM self-correction if errors found
└─────────┬───────────┘
          │
          ▼
       Result
```

---

## External Dependencies

| Dependency | Purpose | Link |
|------------|---------|------|
| BIRD Benchmark | Evaluation dataset (1,534 Text-to-SQL examples, 11 SQLite databases) | https://bird-bench.github.io/ |
| OpenAI API | GPT-4o-mini inference | https://platform.openai.com/ |
| Groq API | Llama-3.1-8b inference (free tier available) | https://console.groq.com/ |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the BIRD dataset

Download the dev set from https://bird-bench.github.io/ and place the contents directly under `data/`:

```
data/
├── dev.json
├── dev_tables.json
└── dev_databases/
    ├── california_schools/
    │   └── california_schools.sqlite
    └── ... (11 databases total)
```

### 3. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

At minimum you need `OPENAI_API_KEY` (GPT-4o-mini) or `GROQ_API_KEY` (Llama 3.1, free tier available).

### 4. Verify setup

```bash
python -c "from data.loader import BirdLoader; l = BirdLoader(); print(f'Loaded {len(l.load())} examples')"
```

Expected: `Loaded 1534 examples`

---

## Usage

### Interactive demo

```bash
python main.py
```

Displays a list of available databases. Enter a database name, then type a natural language question. The pipeline runs all 5 steps and prints intermediate results (filtered schema, CoT reasoning, generated SQL, verification, execution result).

**Example queries to try (all verified correct):**

| # | Question | Database | Evidence | Expected Result |
|---|----------|----------|----------|-----------------|
| 1 | `What is the phone number of the school that has the highest average score in Math?` | `california_schools` | _(leave blank)_ | `(408) 366-7700` |
| 2 | `What is the type of education offered in the school who scored the highest average in Math?` | `california_schools` | _(leave blank)_ | `Traditional` |
| 3 | `How many schools with an average score in Math greater than 400 in the SAT test are exclusively virtual?` | `california_schools` | `Exclusively virtual refers to Virtual = 'F'` | `4` |

Query 3 demonstrates the domain knowledge (Evidence) feature — paste the evidence string when prompted.

### Single query (non-interactive)

```bash
python main.py --question "What is the phone number of the school with the highest average Math score?" --db_id california_schools --verbose
```

### Run experiments

All experiment scripts must be run as modules from the project root:

```bash
# Baseline: direct prompting, no reliability mechanisms
python -m experiments.run_baseline --model openai --limit 100 --output results_baseline.json

# Full pipeline: all three mechanisms
python -m experiments.run_full_pipeline --model openai --limit 100 --output results_full_pipeline.json

# Ablation study: each mechanism individually vs combined
python -m experiments.run_ablation

# Robustness: paraphrase and synonym perturbations
python -m experiments.run_robustness

# Cross-model comparison: GPT-4o-mini vs Llama-3.1-8b
python -m experiments.run_llm_comparison --limit 100
```

`--model` accepts `openai` (GPT-4o-mini) or `groq` (Llama-3.1-8b).

---

## Results

Evaluated on BIRD dev set, 100 examples, comparing Baseline (direct prompting) vs Full Pipeline.

| Model | Mode | EX | Simple | Moderate | Challenging |
|-------|------|----|--------|----------|-------------|
| GPT-4o-mini | Baseline | 24% | 30.5% | 11.4% | 33.3% |
| GPT-4o-mini | Full Pipeline | **26%** | **35.6%** | **14.3%** | 0.0% |
| Llama-3.1-8b | Baseline | 17% | 28.8% | 0.0% | 0.0% |
| Llama-3.1-8b | Full Pipeline | **19%** | 25.4% | **11.4%** | 0.0% |

Ablation study (n=20, GPT-4o-mini):

| Configuration | EX | vs Baseline |
|---------------|----|-------------|
| Baseline | 20% | — |
| Schema only | 50% | +30% |
| CoT only | 40% | +20% |
| Verification only | 20% | 0% |
| Full Pipeline | 45% | +25% |

Robustness under question perturbation (n=20, GPT-4o-mini, Full Pipeline):

| Perturbation | EX | Drop |
|--------------|----|------|
| Original | 40% | — |
| Paraphrase | 30% | −10% |
| Synonym replace | 30% | −10% |

---

## Repository Structure

```
TrustSQL/
├── config.py                    # Model names, dataset paths
├── main.py                      # Interactive demo + single-query entry point
├── notebook.ipynb               # Experiment results and visualizations
├── data/
│   └── loader.py                # BIRD dataset loader (BirdLoader, BirdExample)
├── pipeline/
│   ├── schema_awareness.py      # LLM-driven schema filtering
│   ├── reasoning.py             # Chain-of-thought structural reasoning
│   ├── sql_generator.py         # SQL generation from filtered schema + reasoning
│   └── verification.py          # Syntax check + LLM self-correction
├── llms/
│   ├── base.py                  # Abstract LLM interface (BaseLLM)
│   ├── openai_llm.py            # GPT-4o-mini wrapper
│   ├── groq_llm.py              # Llama-3.1-8b via Groq (with rate-limit retry)
│   └── gemini_llm.py            # Gemini wrapper (implemented, not used in experiments)
├── evaluation/
│   ├── executor.py              # SQLite execution and result comparison
│   ├── metrics.py               # EX accuracy, error classification, difficulty breakdown
│   └── robustness.py            # Question perturbation (paraphrase, synonym)
├── experiments/
│   ├── run_baseline.py          # Baseline experiment
│   ├── run_full_pipeline.py     # Full pipeline experiment
│   ├── run_ablation.py          # Ablation study
│   ├── run_robustness.py        # Robustness experiment
│   └── run_llm_comparison.py   # Cross-model comparison
├── milestones/                  # All course milestone documents including project proposal, revised proposal, progress report, literature review, demo slides, and final report
├── results/                     # Saved experiment JSON outputs for all reported experiments
│   ├── results_baseline_openai_v4.json
│   ├── results_full_pipeline_openai_v4.json
│   ├── results_full_pipeline_groq_v4.json
│   ├── results_comparison.json
│   ├── results_ablation.json
│   └── results_robustness.json
└── figure/                      # Generated figures and demo screenshots
```

---

## Models

| Model | Provider | API |
|-------|----------|-----|
| GPT-4o-mini | OpenAI | `openai` Python SDK |
| Llama-3.1-8b-instant | Meta via Groq | `groq` Python SDK |
| Gemini 2.0 Flash | Google | `google-genai` SDK (not used in experiments due to API quota changes) |

---

## Baseline (Alternative System)

The comparison system used in all evaluations is a **direct prompting baseline**: the full database schema and question are sent directly to the LLM with no schema filtering, no chain-of-thought reasoning, and no verification. This represents the standard approach to Text-to-SQL with LLMs and serves as the alternative system against which TrustSQL is evaluated.

The baseline is implemented in `experiments/run_baseline.py` and uses the same LLM and prompt format as the full pipeline, differing only in the absence of the three reliability mechanisms. All results tables in this repository include side-by-side baseline and full pipeline scores for direct comparison.

---

## Reproducing Experiments

To reproduce the main results from scratch:

```bash
# Step 1: run baseline (GPT-4o-mini, 100 examples)
python -m experiments.run_baseline --model openai --limit 100 --output results/results_baseline_openai.json

# Step 2: run full pipeline (GPT-4o-mini, 100 examples)
python -m experiments.run_full_pipeline --model openai --limit 100 --output results/results_full_pipeline_openai.json

# Step 3: repeat with Llama-3.1-8b (requires GROQ_API_KEY, slower due to rate limits)
python -m experiments.run_baseline --model groq --limit 100 --output results/results_baseline_groq.json
python -m experiments.run_full_pipeline --model groq --limit 100 --output results/results_full_pipeline_groq.json

# Step 4: ablation study (GPT-4o-mini, 20 examples)
python -m experiments.run_ablation

# Step 5: robustness test (GPT-4o-mini, 20 examples)
python -m experiments.run_robustness
```

Then open `notebook.ipynb` and run all cells to reproduce all figures and tables.

> **Note on Groq rate limits:** The free tier is capped at ~6,000 TPM. The Groq wrapper
> includes exponential backoff retry (up to 5 attempts), but a 100-example run may take
> 30–40 minutes. An `OPENAI_API_KEY` is sufficient to reproduce the primary results.

---

## Dataset

**BIRD** (Big Bench for Large-scale Database Grounded Text-to-SQL Evaluation)
- 1,534 examples across 11 real-world SQLite databases
- Difficulty distribution: 925 simple / 464 moderate / 145 challenging
- Includes domain knowledge hints ("evidence") for complex queries
- Download: https://bird-bench.github.io/

---

## AI Tools

This project was developed with the assistance of the following AI tools:

| Tool | Usage |
|------|-------|
| **Claude** (Anthropic) | Used to assist with code debugging and report writing. All experimental results and system design decisions were made by the author. |
| **GPT-4o-mini** (OpenAI) | LLM under evaluation; called at runtime via the OpenAI API |
| **Llama-3.1-8b-instant** (Meta via Groq) | LLM under evaluation; called at runtime via the Groq API |
| **Gemini 2.0 Flash** (Google) | Implemented as a third LLM wrapper but excluded from experiments due to API quota unavailability |
