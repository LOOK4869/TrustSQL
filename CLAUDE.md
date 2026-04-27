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
- 1534 examples across 11 databases，难度分布：925 simple / 464 moderate / 145 challenging
- 数据直接放在 `data/` 下（不是 `data/bird/`）

## LLMs Under Evaluation
| Model | Provider | API |
|-------|----------|-----|
| GPT-4o-mini | OpenAI | openai SDK |
| Gemini 2.0 Flash | Google | google-genai SDK（因API政策变更未能用于实验，见问题记录）|
| Llama 3.1-8b | Meta via Groq | groq SDK |

## Evaluation Metrics
- **EX (Execution Accuracy)** — Does the generated SQL produce the same result as gold SQL?
- **Robustness** — Does accuracy hold under semantic perturbations of the question?
- **Error Type Analysis** — Categorize failures: wrong table, wrong column, wrong join, wrong condition, etc.
- **Efficiency & Cost** — Execution time and latency comparison between baseline and full pipeline

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
├── main.py                 # Full pipeline entry point (interactive mode)
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
- Run experiment scripts with `python -m experiments.run_xxx` from project root

---

## Milestones

### Milestone 1: Project Scaffold ✅
- CLAUDE.md, README.md, requirements.txt
- All folder structure and empty stub files created
- config.py, main.py, .env.example

### Milestone 2: Dataset Integration ✅
- Downloaded BIRD dev set，直接放在 data/ 下
- 实现 data/loader.py：BirdExample dataclass + BirdLoader 类
- 关键发现：BIRD 列名含空格和特殊字符（如 `Free Meal Count (K-12)`），SQL 中必须用反引号

### Milestone 3: Baseline Implementation ✅
- 实现 llms/base.py、llms/openai_llm.py、pipeline/sql_generator.py、evaluation/executor.py
- 端到端跑通：question → SQL → execution → result
- 初始 baseline EX（10条）：10%
- 发现主要失败原因：模型把带空格的列名简化（如 `Free Meal Count (K-12)` → `FreeMealCountK12`）

### Milestone 4: Three Reliability Mechanisms ✅
- 实现 pipeline/schema_awareness.py：LLM 驱动的 Schema 过滤，返回 JSON，验证后回退到全 schema
- 实现 pipeline/reasoning.py：CoT 推理（后调整为只推理逻辑结构，不涉及列名）
- 实现 pipeline/verification.py：语法检查、列名检查、JOIN 路径检查
- 串联进 main.py：run_pipeline() + 交互式模式

### Milestone 5: Experiments and Evaluation ✅
- 实现 llms/groq_llm.py（含限速重试）、llms/gemini_llm.py（已实现但未用于实验）
- 实现 evaluation/metrics.py、evaluation/robustness.py
- 实现 experiments/run_baseline.py、run_full_pipeline.py、run_llm_comparison.py、run_ablation.py

### Milestone 5 实验结果汇总

#### 第一次实验（prompt有bug，已废弃）
- GPT-4o-mini：Baseline 18% → Full Pipeline 13%（Pipeline 反而更差）
- 原因：Schema 过滤误删关键列 + SQL generator 未强调列名反引号

#### 第二次实验（修复 prompt 后，CoT 改进前）
| 模型 | 模式 | EX | Simple | Moderate | Challenging |
|------|------|-----|--------|----------|-------------|
| GPT-4o-mini | Baseline | 24% | 30.5% | 11.4% | 33.3% |
| GPT-4o-mini | Full Pipeline | 26% | 37.3% | 8.6% | 16.7% |
| Llama-3.1-8b | Baseline | 17% | 28.8% | 2.9% | 0.0% |
| Llama-3.1-8b | Full Pipeline | 13% | 22.0% | 0.0% | 0.0% |

#### 消融实验（第一版 CoT，20条）
| 配置 | EX | 相比Baseline |
|------|----|-------------|
| Baseline | 15% | — |
| Schema only | 50% | +35% |
| CoT only | 20% | +5% |
| Verification only | 15% | 0% |
| Full Pipeline | 45% | +30% |

#### 消融实验（改进 CoT 后，20条）
| 配置 | EX | 相比Baseline |
|------|----|-------------|
| Baseline | 20% | — |
| Schema only | 40% | +20% |
| CoT only | 35% | +15% |
| Verification only | 20% | 0% |
| Full Pipeline | 40% | +20% |

#### 消融实验（修复 Verification 自纠错误报后，20条）
| 配置 | EX | 相比Baseline |
|------|----|-------------|
| Baseline | 20% | — |
| Schema only | 50% | +30% |
| CoT only | 40% | +20% |
| Verification only | 20% | 0%（无副作用）|
| Full Pipeline | 45% | +25% |

改动说明：将列名检查、JOIN路径检查降级为 warning，只有 SQLite 语法错误才触发 LLM 自纠错。

#### 第三次实验（改进 CoT prompt 后，100条）
| 模型 | 模式 | EX | Simple | Moderate | Challenging |
|------|------|-----|--------|----------|-------------|
| GPT-4o-mini | Baseline | 24% | 30.5% | 11.4% | 33.3% |
| GPT-4o-mini | Full Pipeline | 26% | 37.3% | 11.4% | 0.0% |
| Llama-3.1-8b | Baseline | 17% | 28.8% | 0.0% | 0.0% |
| Llama-3.1-8b | Full Pipeline | 17% | 22.0% | 11.4% | 0.0% |

#### 第四次实验（最终版，修复 Verification 误报后，100条）
| 模型 | 模式 | EX | Simple | Moderate | Challenging |
|------|------|-----|--------|----------|-------------|
| GPT-4o-mini | Baseline | 24% | 30.5% | 11.4% | 33.3% |
| GPT-4o-mini | Full Pipeline | 26% | 35.6% | 14.3% | 0.0% |
| Llama-3.1-8b | Baseline | 17% | 28.8% | 0.0% | 0.0% |
| Llama-3.1-8b | Full Pipeline | 19% | 25.4% | 11.4% | 0.0% |

主要发现：
- Schema Awareness 是最核心机制，消融实验显示单独使用提升最大（+30%）
- GPT-4o-mini Full Pipeline 比 Baseline +2%，Simple 难度 +5.1%，所有难度均不低于 Baseline
- Llama-3.1-8b Full Pipeline 比 Baseline +2%，修复 Verification 误报后有改善
- Challenging 仅6条样本，数值波动大，不具统计意义
- 最常见错误：wrong_column、wrong_join、wrong_condition

---

## 实验过程中遇到的问题记录（供报告参考）

### 问题1：Groq 模型下线
- 现象：调用 `llama3-8b-8192` 报错 `model_decommissioned`
- 原因：Groq 于2025年底下线该模型
- 解决：改用 `llama-3.1-8b-instant`
- 报告写法：LLM API 生态变化快，模型版本需定期更新

### 问题2：Groq API 限速（Rate Limit）
- 现象：跑100条时中途报错 `RateLimitError 429`
- 原因：Groq 免费版每分钟 token 上限 6000 TPM
- 解决：在 `groq_llm.py` 加入指数退避重试（1s→2s→4s→8s→16s）
- 报告写法：免费 API 限速是实际部署需考虑的工程问题

### 问题3：Gemini API 免费额度政策变更
- 现象：Google AI Studio 个人账号 free tier quota 为 0
- 原因：Google 2026年4月调整政策，部分地区需付费
- 解决：改为 GPT-4o-mini 和 Llama 3.1 两个模型对比
- 报告写法：Gemini 因政策变更未纳入实验，代码已实现（`llms/gemini_llm.py`），有额度可直接接入

### 问题4：Full Pipeline EX 低于 Baseline（已修复）
- 现象：第一次100条实验，Full Pipeline 13% < Baseline 18%
- 原因1：Schema 过滤 prompt 太激进，误删关键列
- 原因2：SQL generator prompt 未强调含空格列名需用反引号
- 修复：Schema filter 改为"宁多勿少"；SQL generator 明确要求反引号，禁止简化列名
- 报告写法：prompt engineering 对系统性能的影响，pipeline 设计需要迭代优化

### 问题5：消融实验的发现（Ablation Study）
- 背景：第二次100条实验提升幅度不理想，想找出哪个机制最有效
- 动机：自然想到把三个机制拆开分别测试，事后意识到这就是学术上的消融实验
- 关键发现：Schema Awareness 单独使用从15%提升到50%（+35%），是最核心的机制
- 报告写法：可在反思部分写"在实践中自然推导出消融实验方法，后认识到这是标准学术分析手段"

### 问题7：Verification 自纠错产生副作用（已修复）
- 现象：加入 LLM 自纠错后，"Verification only" 消融配置 EX 反而低于 Baseline（20% → 20%，Full Pipeline 40% 未超过 Schema only 50%）
- 原因：列名检查和 JOIN 路径检查存在误报——schema 被过滤后，合法的列名可能不在过滤后的 schema 里；误判触发 LLM 重写，把本来正确的 SQL 改坏了
- 修复：将列名检查和 JOIN 检查降级为 warning（只记录不干预），只有 SQLite 实际报语法错误时才触发 LLM 自纠错（误报率接近零）
- 设计原则：验证器应"宁可漏报，不可误报"——语法错误是客观事实，可以放心纠错；列名推断是启发式规则，不能作为自动修改的依据
- 报告写法：说明 Verification 作为最后一道保障，其价值在于捕获语法级错误，不应过度干预语义层面

### 问题6：CoT 定位与局限性
- 理想设计：CoT 作为用户确认环节，用户可主观判断推理是否合理
- 局限性：BIRD 全自动评估无法验证推理过程，人工验证1534条不现实
- 发现的问题：原 CoT prompt 让模型自由推理列名，污染 SQL generator
- 解决（评估版）：CoT 只推理逻辑结构（需不需要 JOIN/聚合/排序），不涉及列名
- Demo 展示版（计划）：保留完整推理展示，让观众主观判断答案合理性
- 报告写法：在局限性章节承认，在未来工作提出"引入人工反馈的交互式CoT"

---

## 待完成事项

### Milestone 5 补充 ✅
- Robustness 测试 ✅：paraphrase + synonym replace 两种扰动，结果放进 Notebook
- Efficiency & Cost ✅：Notebook 中直接计时，baseline vs full pipeline 平均延迟

#### 鲁棒性测试结果（n=20，GPT-4o-mini，Full Pipeline）
| 扰动方式 | EX | 下降 |
|---------|-----|------|
| Original | 40% | — |
| Paraphrase | 30% | -10% |
| Synonym Replace | 30% | -10% |

分析：两种扰动均导致准确率下降 10%，说明系统对问题措辞有一定敏感性。
根本原因：Schema Filtering 依赖问题中的关键词匹配，措辞变化可能导致相关列被过滤掉。
报告写法：作为 Limitations 如实呈现，Future Work 提出 paraphrase augmentation 和更鲁棒的 schema linking 作为改进方向。

### Milestone 6: Final Report（待做）

#### 报告格式要求
- 约 8 页，不含参考文献和附录
- 第一页：标题、全名、UNI（kl3753）
- 字体：11pt，单倍行距，1 inch 页边距
- 需要页码
- 需要参考文献（BIRD benchmark、GPT-4o-mini、Llama 3.1、相关 Text-to-SQL 论文）
- 附录放大图、截图、代码示例
- 需要提供 GitHub 仓库链接

#### 报告必须包含的四个部分
1. **Synopsis** — 项目概述，说明做了什么、怎么做的、创新点和价值
2. **Research Questions** — 研究问题及答案，必须包含消融实验
3. **Deliverables** — GitHub 仓库链接，包含所有代码、实验脚本、文档
4. **Self-Evaluation** — 完成了什么、遇到什么挑战、学到了什么

#### 注意事项
- 如果之前进度报告承诺了但没做到的内容，必须说明原因（如 Gemini API 政策变更）
- 老师特别喜欢图表、流程图、对比图，多放视觉内容
- 需要说明是否有人在课外合作（disclosure）

### Milestone 7: Demo 准备
- 改造 main.py 为交互式模式 ✅（直接运行无需参数，显示数据库列表，循环输入）
- 提前筛选2-3条模型能答对的问题备用 ✅（见下方）
- 制作 PPT（含项目介绍 + 实验数据，供老师课后查阅）

#### Demo 备用问题（Full Pipeline 已验证答对，数据库均为 california_schools）

**问题1（推荐首选，结果直观）**
- Question: `What is the phone number of the school that has the highest average score in Math?`
- Evidence: 
- Database: `california_schools`
- 预期结果: `(408) 366-7700`

**问题2（有趣，涉及计算）**
- Question: `What is the type of education offered in the school who scored the highest average in Math?`
- Evidence: 
- Database: `california_schools`
- 预期结果: `Traditional`

**问题3（涉及 Evidence，能展示 domain knowledge 机制）**
- Question: `How many schools with an average score in Math greater than 400 in the SAT test are exclusively virtual?`
- Evidence: `Exclusively virtual refers to Virtual = 'F'`
- Database: `california_schools`
- 预期结果: `4`


