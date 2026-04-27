# TrustSQL Demo Script

## Part 1 — PPT Introduction (1 min)

**Slide 1 (Title)**
> "Hi everyone, today I will present TrustSQL — a Text-to-SQL pipeline."

**Slide 2 (System Overview)**
> "The core problem is that LLMs often generate wrong SQL when facing large, noisy real-world databases — wrong column names, missing JOINs, incorrect conditions.
>
> TrustSQL solves this with a 3-stage pipeline. First, Schema Awareness filters out irrelevant tables and columns so the model only sees what it needs. Second, Chain-of-Thought Reasoning plans the query logic before writing any SQL. Third, Verification checks the generated SQL for syntax errors and automatically self-corrects if needed.
>
> Let me show you how this works in practice."

---

## Part 2 — Live Demo (3 min)

### 操作步骤

1. **切换到终端**（提前打开好，在项目目录下）
2. 运行：
   ```
   python main.py
   ```
3. 看到数据库列表后，输入问题：
   ```
   Question: What is the phone number of the school that has the highest average score in Math?
   Database ID: california_schools
   Evidence: （直接回车跳过）
   ```
4. 等待输出，边等边讲解每个步骤在做什么

### 讲解词（对应每个 Step 输出时说）

> "So the system is now running the full pipeline."

**Step 1 出现时：**
> "Step 1 — Schema Filtering. The model looked at the full database schema and kept only the relevant tables and columns. Here it identified the `satscores` and `schools` tables, and only the columns needed to answer this question."

**Step 2 出现时：**
> "Step 2 — Chain-of-Thought Reasoning. Before writing any SQL, the system plans the logic: we need a single value, we need to JOIN two tables, we need aggregation to compute the average, and sorting to find the highest."

**Step 3 出现时：**
> "Step 3 — SQL Generation. Based on the filtered schema and the reasoning, the model generates the SQL query."

**Step 4 出现时：**
> "Step 4 — Verification. The system checks the SQL for syntax errors. If there's a problem, it automatically self-corrects."

**Step 5 出现时：**
> "Step 5 — Execution. The SQL runs against the local SQLite database and returns the result."

**结果出来后：**
> "The answer is (408) 366-7700. This is the correct answer verified against the gold standard SQL."

---

## Part 3 — Notebook Results (2 min)

### 操作步骤

1. **切换到浏览器**，打开已经跑好的 Jupyter Notebook
2. 从上往下滚动展示图表，不需要重新运行

### 讲解词

**Overall Accuracy 图：**
> "We evaluated on 100 examples from the BIRD benchmark. GPT-4o-mini improved from 24% to 26%, and Llama-3.1-8b from 17% to 19%. Both models benefit from the pipeline."

**By Difficulty 图：**
> "Breaking it down by difficulty — the improvement is most significant on Simple questions. For Llama, the Moderate accuracy jumped from 0% to 11.4%, showing that the pipeline helps smaller models handle more complex queries."

**Error Distribution 图：**
> "The most common failure types are wrong column, wrong join, and wrong condition — these are exactly the issues our three mechanisms are designed to address."

**Latency 图：**
> "The full pipeline takes about 3-4x longer per query compared to baseline. This is the cost of running four LLM calls instead of one — a reasonable trade-off for the accuracy gain."

**最后总结一句：**
> "To summarize: Schema Awareness is the most impactful single mechanism, CoT reasoning provides additional structure, and Verification acts as a safety net. Together they consistently outperform the baseline across both models. Thank you."

---

## 展示前检查清单

- [ ] 终端已打开，`cd` 到 TrustSQL 目录
- [ ] `.env` 文件里 API key 有效（OpenAI 余额充足）
- [ ] Jupyter Notebook 已在浏览器中打开，所有 cell 已跑完
- [ ] 网络连接正常
- [ ] 屏幕共享测试过，字体大小观众能看清
