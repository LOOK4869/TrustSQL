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

## Milestones

### Milestone 1: Project Scaffold ✅
- CLAUDE.md, README.md, requirements.txt
- All folder structure and empty stub files created
- config.py, main.py, .env.example

### Milestone 2: Dataset Integration ✅
- Downloaded BIRD dev set from https://bird-bench.github.io (placed directly under data/, not data/bird/)
- Implemented data/loader.py: BirdExample dataclass + BirdLoader class
  - load() reads dev.json → 1534 examples across 11 databases
  - get_schema() uses dev_tables.json (column_names_original) as primary source, falls back to SQLite PRAGMA
  - get_foreign_keys() parses dev_tables.json foreign_keys index pairs
  - get_db_path() returns path to per-database .sqlite file
- Dataset stats: 925 simple / 464 moderate / 145 challenging
- Key finding: BIRD column names contain spaces and special chars (e.g. `Free Meal Count (K-12)`) — must be quoted with backticks in SQL

### 实验过程中遇到的问题记录（供报告参考）

#### 问题1：Groq API 限速（Rate Limit）
- 现象：使用 Llama 3.1（via Groq）跑100条样本时，实验中途报错 `RateLimitError 429`
- 原因：Groq 免费版每分钟 token 上限为 6000 TPM，连续请求超额
- 解决方案：在 `groq_llm.py` 中加入指数退避重试机制（1s → 2s → 4s → 8s → 16s）
- 报告写法：可在 Efficiency & Cost 章节提及，免费 API 的速率限制是实际部署中需要考虑的工程问题，付费版可解决

#### 问题2：Groq 模型下线
- 现象：原计划使用 `llama3-8b-8192`，调用时报错 `model_decommissioned`
- 原因：Groq 于2025年底下线了该模型
- 解决方案：改用 `llama-3.1-8b-instant`
- 报告写法：说明 LLM API 生态变化较快，模型版本需定期更新

#### 问题3：Gemini API 免费额度政策变更
- 现象：Google AI Studio 个人账号 free tier quota 为 0，无法免费调用
- 原因：Google 于2026年4月调整政策，部分地区需付费才能使用
- 解决方案：项目改为使用 GPT-4o-mini 和 Llama 3.1 两个模型进行对比
- 报告写法：说明 Gemini 因 API 政策变更未能纳入实验，但代码层面已完整实现（`llms/gemini_llm.py`），如获得访问权限可直接接入

### Gemini API 集成说明（2026年4月）
- 尝试使用 Google AI Studio 个人账号（look4869128@gmail.com）获取 Gemini 免费 API
- 历史上 Gemini API 提供每日免费额度（free tier），但 2026年4月政策已变更
- 现在免费层级 quota 为 0，必须购买点数（最低 $25）才能调用 API
- 项目决定跳过 Gemini，使用 GPT-4o-mini（OpenAI）和 Llama 3.1（Groq）两个模型进行实验
- 报告说明：Gemini 因 API 政策变更无法免费使用，实验在 GPT-4o-mini 和 Llama 3.1 上进行对比
- 技术上 GeminiLLM 封装已完整实现（llms/gemini_llm.py），如后续获得 API 额度可直接接入

### Milestone 3: Baseline Implementation ✅
- Implemented llms/base.py: abstract BaseLLM with complete() and chat() methods
- Implemented llms/openai_llm.py: GPT-4o-mini via openai SDK
- Implemented pipeline/sql_generator.py: prompt → LLM → SQL extraction via regex (```sql blocks)
- Implemented evaluation/executor.py: SQLite sandboxed execution + order-independent result comparison
- End-to-end verified: question → SQL → execution → result
- **Baseline EX result (10 samples): 1/10 = 10%**
- Key failure mode observed: model strips spaces from column names (e.g. `Free Meal Count (K-12)` → `FreeMealCountK12`), causing "no such column" errors
- This motivates Milestone 4: Schema Awareness will inject exact column names into the prompt

### Milestone 4: Three Reliability Mechanisms ✅
- Implemented pipeline/schema_awareness.py: LLM-based schema filtering, returns JSON of relevant tables/columns, validated against full schema, falls back to full schema if parsing fails
- Implemented pipeline/reasoning.py: 6-step CoT prompt (SELECT target → tables → JOINs → WHERE → aggregations → ORDER/LIMIT)
- Implemented pipeline/verification.py: three checks — SQLite EXPLAIN syntax check, backtick column name validation, multi-table JOIN path warning
- Connected all three into main.py: run_pipeline() function with verbose mode
- Small-scale result (10 samples): Baseline 10% → Full Pipeline 20% (+10%)
- Key observation: Schema filtering correctly prunes irrelevant tables; CoT reasoning improves JOIN identification; column name errors remain the dominant failure mode

### Milestone 5: Experiments and Evaluation
- Implement llms/gemini_llm.py and llms/groq_llm.py
- Implement evaluation/metrics.py and evaluation/robustness.py
- Run experiments/run_baseline.py and experiments/run_full_pipeline.py
- Run experiments/run_llm_comparison.py across all three LLMs

### Milestone 6: Results and Final Report
- Generate comparison tables
- Error type analysis
- Write final report

### Milestone 6 补充：Robustness 测试（待实现，最后统一跑）
- 等所有代码确认没问题后，最后跑一次 robustness.py
- 测试 paraphrase（改写问题）和 synonym replace（同义词替换）两种扰动
- 结果放进最终 Notebook 的对比表格
- 目的：控制 API 消费，集中在最后一次跑完所有测试

### Milestone 6 补充：Efficiency & Cost 计时（待实现）
- 在实验脚本里加计时功能，记录每条查询的耗时
- 对比 baseline 和 full pipeline 的平均延迟
- 对应论文 4.4 节 Efficiency and Cost

### Milestone 5 实验结果（100条样本）
| 模型 | 模式 | EX准确率 | simple | moderate | challenging |
|------|------|---------|--------|----------|-------------|
| GPT-4o-mini | Baseline | 18% | 22.0% | 14.3% | 0.0% |
| GPT-4o-mini | Full Pipeline | 13% | 15.3% | 8.6% | 16.7% |
| Llama-3.1-8b | Baseline | 12% | 18.6% | 2.9% | 0.0% |
| Llama-3.1-8b | Full Pipeline | 10% | 16.9% | 0.0% | 0.0% |

主要发现：
- GPT-4o-mini 整体优于 Llama 3.1
- Full Pipeline 对 challenging 难度有帮助（GPT 0%→16.7%）
- Full Pipeline 总体 EX 略低于 Baseline，原因是 Schema 过滤有时误删关键列，导致 wrong_column 错误增多
- 最常见错误：wrong_column（列名问题）和 wrong_condition（条件写错）
- 需要分析并在报告中讨论为何 full pipeline EX 低于 baseline（prompt设计问题，schema过滤过激）

### Milestone 7: Demo 准备（待实现）
- 改造 main.py 为交互式模式：直接运行 `python main.py` 无需任何参数
- 终端显示可用数据库列表，用户输入数字选择
- 用户直接输入自然语言问题按回车，流水线自动执行
- 展示每一步中间结果（Schema过滤 → CoT推理 → SQL生成 → 验证 → 执行结果）
- 提前筛选2-3条模型能答对的问题，现场跑有把握

**Demo现场流程（共6分钟）：**
1. 1分钟：PPT介绍项目（是什么、三个机制）
2. 3分钟：现场跑 main.py（交互式，2-3条问题）
3. 2分钟：切换到 Notebook 展示实验数据和图表

**提交内容：**
- PPT（含项目介绍 + 实验数据图表，供老师课后查阅）
- Notebook（现场展示用）
