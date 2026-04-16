
# TrustSQL: A Reliability-Oriented Text-to-SQL Pipeline

## Overview

TrustSQL is a research project investigating how to improve the **reliability** of LLM-generated SQL queries on real-world databases. Rather than simply prompting a model and hoping for the best, TrustSQL introduces three structured mechanisms that work together in a pipeline:

1. **Schema Awareness** — Prune irrelevant tables and columns before generation
2. **Knowledge & Reasoning** — Elicit chain-of-thought reasoning to guide SQL construction
3. **Guardrails & Verification** — Validate generated SQL before execution

Evaluated on the [BIRD benchmark](https://bird-bench.github.io/) across three LLMs: GPT-4o-mini, Gemini 1.5 Flash, and Llama 3 (via Groq).

---

## Research Questions

- Does schema filtering improve execution accuracy on databases with many tables/columns?
- Does chain-of-thought reasoning reduce structural SQL errors?
- Does post-generation verification catch and correct common failure modes?
- How do the three LLMs compare in reliability, not just raw accuracy?

---

## Pipeline Architecture

```
User Question
     │
     ▼
┌─────────────────────┐
│  Schema Awareness   │  ← Filter relevant tables & columns
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  CoT Reasoning      │  ← Decompose question into reasoning steps
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  SQL Generation     │  ← LLM generates SQL from filtered schema + reasoning
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Verification       │  ← Check validity, columns, join paths
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Execution & Score  │  ← Run SQL, compare to gold, record metrics
└─────────────────────┘
```

---

## Project Structure

```
trustsql/
├── CLAUDE.md                   # Project context for Claude Code
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── config.py                   # API keys, model names, dataset paths
├── main.py                     # Entry point: run full pipeline on a query
├── data/
│   └── loader.py               # Load BIRD dataset: questions, schemas, gold SQL
├── pipeline/
│   ├── schema_awareness.py     # Filter relevant tables and columns
│   ├── reasoning.py            # Generate intermediate CoT reasoning steps
│   ├── sql_generator.py        # Call LLM to generate SQL
│   └── verification.py         # Validate SQL before execution
├── llms/
│   ├── base.py                 # Abstract LLM interface
│   ├── openai_llm.py           # GPT-4o-mini wrapper
│   ├── gemini_llm.py           # Gemini 1.5 Flash wrapper
│   └── groq_llm.py             # Llama 3 via Groq wrapper
├── evaluation/
│   ├── executor.py             # Execute SQL, return results
│   ├── metrics.py              # EX accuracy, error type analysis
│   └── robustness.py           # Semantic perturbations for robustness testing
└── experiments/
    ├── run_baseline.py         # Baseline: direct prompting, no reliability mechanisms
    ├── run_full_pipeline.py    # Full pipeline with all three mechanisms
    └── run_llm_comparison.py  # Cross-LLM comparison on same queries
```

---

## Dataset

This project uses the **BIRD** (Big Bench for Large-scale Database Grounded Text-to-SQL) benchmark.

> ⚠️ **The dataset is NOT included in this repository** (files are too large for GitHub).
> You must download it manually before running any code.

**Download steps:**
1. Go to https://bird-bench.github.io/
2. Click the **Dev Set** button to download the dataset
3. Unzip and place the contents directly under `data/` so the structure looks like:

```
data/
├── dev.json
├── dev_tables.json
├── dev_databases/
│   ├── california_schools/
│   │   └── california_schools.sqlite
│   ├── card_games/
│   │   └── card_games.sqlite
│   └── ... (11 databases total)
└── loader.py
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the BIRD dataset

See the **Dataset** section above. Make sure `data/dev.json` and `data/dev_databases/` exist before proceeding.

### 3. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
```

At minimum, you need either `OPENAI_API_KEY` (GPT-4o-mini) or `GROQ_API_KEY` (Llama 3.1, free) to run the pipeline.

### 4. Verify the dataset loads correctly

```bash
python -c "
from data.loader import BirdLoader
loader = BirdLoader()
examples = loader.load()
print(f'Loaded {len(examples)} examples across {len(set(e.db_id for e in examples))} databases')
"
```

Expected output: `Loaded 1534 examples across 11 databases`

### 5. Run interactive demo

```bash
python main.py
```

Select a database from the menu, then type any natural language question. The pipeline will run through all 5 steps and return the answer.

### 6. Run a single query (non-interactive)

```bash
python main.py --question "How many superheroes have blue eyes?" --db_id "superhero" --verbose
```

### 7. Run experiments

```bash
# Baseline (direct prompting, no reliability mechanisms)
python -m experiments.run_baseline --model openai --limit 100

# Full pipeline (all three mechanisms)
python -m experiments.run_full_pipeline --model openai --limit 100

# Cross-LLM comparison (GPT-4o-mini vs Llama 3.1)
python -m experiments.run_llm_comparison --limit 100
```

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **EX (Execution Accuracy)** | Fraction of queries where generated SQL produces identical results to gold SQL |
| **Robustness** | EX score under semantic perturbations (paraphrasing, synonym replacement) |
| **Error Type Analysis** | Breakdown of failures by category: wrong table, wrong column, wrong join, wrong condition, etc. |

---

## Models

| Model | Provider | Notes |
|-------|----------|-------|
| `gpt-4o-mini` | OpenAI | Cost-efficient, strong reasoning |
| `gemini-1.5-flash` | Google | Fast inference, multimodal capable |
| `llama3-8b-8192` | Meta via Groq | Open-weight, fast via Groq API |

---

## License

For academic research use. See individual model and dataset licenses for usage restrictions.

---

---

# TrustSQL：面向可靠性的 Text-to-SQL 流水线

## 项目简介

TrustSQL 是一个研究项目，旨在提升大语言模型（LLM）在真实数据库上生成 SQL 查询的**可靠性**。不同于直接提示模型生成 SQL，TrustSQL 引入了三个结构化机制，形成完整的处理流水线：

1. **Schema 感知** — 在生成前过滤无关的表和列
2. **知识与推理** — 通过链式思考引导 SQL 构建
3. **防护与验证** — 在执行前对生成的 SQL 进行合法性校验

在 [BIRD 基准](https://bird-bench.github.io/) 上，对三个 LLM 进行评估：GPT-4o-mini、Gemini 1.5 Flash 和 Llama 3（通过 Groq）。

---

## 研究问题

- Schema 过滤是否能提升含有大量表/列的数据库上的执行准确率？
- 链式思考推理是否能减少 SQL 结构性错误？
- 后生成验证是否能捕获并修正常见的失败模式？
- 三个 LLM 在可靠性（而非单纯准确率）方面表现如何？

---

## 流水线架构

```
用户问题
     │
     ▼
┌─────────────────────┐
│  Schema 感知模块    │  ← 过滤相关表和列
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  链式思考推理       │  ← 将问题分解为推理步骤
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  SQL 生成           │  ← LLM 基于过滤后的 Schema 和推理链生成 SQL
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  验证模块           │  ← 检查语法、列名、关联路径
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  执行与评分         │  ← 运行 SQL，与标准答案比较，记录指标
└─────────────────────┘
```

---

## 项目结构

```
trustsql/
├── CLAUDE.md                   # Claude Code 项目上下文
├── README.md                   # 本文件
├── requirements.txt            # Python 依赖
├── config.py                   # API 密钥、模型名称、数据集路径
├── main.py                     # 入口：对单条查询运行完整流水线
├── data/
│   └── loader.py               # 加载 BIRD 数据集：问题、Schema、标准 SQL
├── pipeline/
│   ├── schema_awareness.py     # 过滤相关表和列
│   ├── reasoning.py            # 生成中间链式推理步骤
│   ├── sql_generator.py        # 调用 LLM 生成 SQL
│   └── verification.py         # 执行前验证 SQL
├── llms/
│   ├── base.py                 # 抽象 LLM 接口
│   ├── openai_llm.py           # GPT-4o-mini 封装
│   ├── gemini_llm.py           # Gemini 1.5 Flash 封装
│   └── groq_llm.py             # Llama 3 via Groq 封装
├── evaluation/
│   ├── executor.py             # 执行 SQL，返回结果
│   ├── metrics.py              # EX 准确率、错误类型分析
│   └── robustness.py           # 语义扰动鲁棒性测试
└── experiments/
    ├── run_baseline.py         # 基线实验：直接提示，无可靠性机制
    ├── run_full_pipeline.py    # 完整流水线实验
    └── run_llm_comparison.py  # 跨 LLM 对比实验
```

---

## 数据集

本项目使用 **BIRD**（面向大规模数据库的 Text-to-SQL 大型基准）数据集。

- 下载地址：https://bird-bench.github.io/
- 将数据直接放置于 `data/` 目录下（注意：不是 `data/bird/`，路径配置见 `config.py`）

---

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

将 `.env.example` 复制为 `.env` 并填写密钥：

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
```

### 3. 对单条查询运行完整流水线

```bash
python main.py --question "有多少歌手来自法国？" --db_id "concert_singer"
```

### 4. 运行实验

```bash
# 基线（无可靠性机制）
python experiments/run_baseline.py

# 完整流水线
python experiments/run_full_pipeline.py

# LLM 对比
python experiments/run_llm_comparison.py
```

---

## 评估指标

| 指标 | 说明 |
|------|------|
| **EX（执行准确率）** | 生成 SQL 与标准 SQL 产生相同结果的查询比例 |
| **鲁棒性** | 在语义扰动（改写、同义词替换）下的 EX 分数 |
| **错误类型分析** | 按类别统计失败：错误的表、错误的列、错误的关联、错误的条件等 |

---

## 使用模型

| 模型 | 提供商 | 备注 |
|------|--------|------|
| `gpt-4o-mini` | OpenAI | 性价比高，推理能力强 |
| `gemini-1.5-flash` | Google | 推理速度快，支持多模态 |
| `llama3-8b-8192` | Meta via Groq | 开源权重，通过 Groq API 快速推理 |
