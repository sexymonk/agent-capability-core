# Workflow Training Manual / 工作流训练教练手册

Use this handbook to coach someone through **training, stabilizing, and freezing** a reusable workflow.

用这份手册指导他人完成 **训练、稳定、固化** 一套可复用 workflow。

---

## 1) Purpose / 目标

- **中文**：帮助教练把“多轮纠正后的做法”提炼成可复用的 workflow、模板或技能。
- **English**: Help a coach turn “a process refined through repeated corrections” into a reusable workflow, template, or skill.

- **中文**：这份手册既指导如何训练 workflow，也指导如何把训练方法本身持续改进。
- **English**: This handbook covers both how to train workflows and how to keep improving the training method itself.

---

## 2) When to use this manual / 何时使用本手册

- **中文**：当用户不只是想完成一次任务，而是想把流程沉淀下来时使用。
- **English**: Use this when the user wants more than one successful run and wants the process itself to be reusable.

- **中文**：当一个流程已经经历了多轮纠正、补充规则、明确 stop/escalation 条件后，适合启动固化。
- **English**: Start solidification after the workflow has accumulated repeated corrections, added rules, and explicit stop/escalation conditions.

---

## 3) Core coaching loop / 核心训练闭环

### Step 1 — Observe the pattern / 观察模式
- **中文**：先区分“用户是在纠正一次执行”，还是“用户在训练一套长期流程”。
- **English**: First distinguish between “fixing one run” and “teaching a durable process”.

### Step 2 — Extract durable rules / 提炼长期规则
- **中文**：把可复用规则和一次性偏好分开。
- **English**: Separate reusable rules from one-off preferences.

### Step 3 — Build the state model / 构建状态机
- **中文**：明确 phase、mode、升级条件、停止条件、人审触发条件。
- **English**: Make the phases, modes, escalation triggers, stop states, and human-review triggers explicit.

### Step 4 — Define artifacts and evidence / 定义产物与证据
- **中文**：规定每一轮、每一阶段必须产出什么材料。
- **English**: Define what artifacts must exist after each round or phase.

### Step 5 — Freeze into reusable assets / 固化为可复用资产
- **中文**：把规则写入 skill，把模板写入 references，把运行态留在 run-local state。
- **English**: Put operating rules into the skill, scaffolds into references, and temporary execution state into run-local state.

### Step 6 — Reflect and self-update / 反思并自我更新
- **中文**：如果本次训练还改进了“如何训练 workflow”，就回写到元技能和手册。
- **English**: If the session improved “how to train workflows”, write that learning back into the meta-skill and the manual.

---

## 4) What to extract from the conversation / 需要从对话中提炼什么

### A. Trigger phrases / 触发语
- **中文**：哪些用户表达意味着“开始训练/固化流程”？
- **English**: Which user phrasings should trigger workflow training or solidification?

### B. Objective / 目标
- **中文**：流程最终要稳定达成什么结果？
- **English**: What stable outcome ends the workflow?

### C. State model / 状态机
- **中文**：有哪些阶段、模式、升级态、回退态？
- **English**: What phases, modes, escalation states, and fallback states exist?

### D. Agent matrix / 代理矩阵
- **中文**：不同阶段由哪些 agent 参与，哪些必须跳过？
- **English**: Which agents participate in each phase, and which must be skipped?

### E. Evidence schema / 证据结构
- **中文**：每轮需要哪些报告、截图、日志、结构化字段？
- **English**: What reports, screenshots, logs, and structured fields are required per round?

### F. Escalation and stop rules / 升级与停止规则
- **中文**：什么条件触发升级？什么条件下可以停止？
- **English**: What conditions escalate the workflow? What conditions allow it to stop?

### G. Human-review loop / 人工复核闭环
- **中文**：何时申请人工检查？人工反馈回来后流程怎么变？
- **English**: When should human review be requested, and how does the workflow change after feedback returns?

### H. Reflection sinks / 反思写回落点
- **中文**：哪些更新属于 workflow skill，哪些属于领域 memory，哪些只属于本次 run？
- **English**: Which updates belong in the workflow skill, which in domain memory, and which only in the current run?

---

## 5) Rule separation model / 规则分层模型

### Generic workflow template / 通用流程模板
- state machine / 状态机
- escalation gates / 升级门槛
- stop rules / 停止规则
- human-review aftermath / 人审后的动作
- reflection writeback / 反思写回

### Domain-specific defaults / 领域默认项
- solver-specific checks / solver 特定检查点
- scene/tool priorities / 场景或工具重点
- domain correctness rules / 领域正确性规则

### Run-local state / 当前运行态
- current round id / 当前轮次
- temporary ROI or hypothesis / 临时 ROI 或假设
- one-off capture settings / 一次性抓图参数

**Rule of thumb / 经验法则**
- **中文**：如果一条规则离开当前领域仍然成立，它更可能是通用模板。
- **English**: If a rule still makes sense outside the current domain, it is probably generic.

---

## 6) Freeze-readiness checklist / 可固化检查表

Only freeze the workflow when most answers are clear.

只有大部分问题都清楚时，才应正式固化 workflow。

- **中文**：流程何时开始？
- **English**: When does the workflow start?
- **中文**：流程有哪些稳定阶段？
- **English**: What are its stable phases?
- **中文**：什么条件触发升级？
- **English**: What triggers escalation?
- **中文**：什么条件允许停止？
- **English**: What allows it to stop?
- **中文**：每轮必须有什么产物？
- **English**: What artifacts must exist after each round?
- **中文**：人工复核何时发生？
- **English**: When does human review happen?
- **中文**：人工确认/否定后要学到什么？
- **English**: What must be learned after human confirmation/correction?
- **中文**：哪些规则是通用的，哪些是领域特有的？
- **English**: Which rules are generic and which are domain-specific?

If several answers are still vague, keep training instead of freezing.

如果还有多项模糊，就继续训练，不要急着固化。

---

## 7) Bilingual design rules / 双语设计规则

- **中文**：保留稳定的**规范状态名**，避免中英文两套名字各自漂移。
- **English**: Keep **canonical state names** stable so the Chinese and English descriptions do not drift apart.

- **中文**：适合长期复用的流程，优先同时提供中文说明和英文说明。
- **English**: For workflows meant for long-term reuse, prefer paired Chinese and English explanations.

- **中文**：如果原始领域术语已有固定英文名，优先保留原术语，再加中文解释。
- **English**: When a domain already has canonical English terminology, keep the original term and add Chinese explanation.

- **中文**：翻译说明应帮助迁移，不应制造两套互相矛盾的规则。
- **English**: Translation should improve transferability, not create two conflicting rule sets.

---

## 8) Example coaching dialogue templates / 示例教练对话模板

### Template A — Start workflow training / 开启 workflow 训练

**Coach / 教练**
- **中文**：你现在是在纠正一次执行，还是想把这套流程长期固定下来？
- **English**: Are you correcting one execution, or do you want this process fixed as a reusable long-term workflow?

**Desired signal / 目标信号**
- **中文**：用户开始描述“以后都要这样做”“把这个流程固定下来”。
- **English**: The user starts saying “do it this way from now on” or “freeze this process”.

---

### Template B — Extract durable rule / 提炼长期规则

**Coach / 教练**
- **中文**：你这条纠正是当前案例特有，还是以后同类任务都适用？
- **English**: Is this correction specific to the current case, or should it apply to future tasks of the same kind?

**Follow-up / 追问**
- **中文**：如果以后遇到不同场景，这条规则还成立吗？
- **English**: Would this rule still hold in a different scenario later?

---

### Template C — Separate generic vs domain / 区分通用规则与领域规则

**Coach / 教练**
- **中文**：这条要求属于流程组织方式，还是属于某个 solver / 工具 / 场景的特定机制？
- **English**: Does this requirement belong to workflow orchestration, or to a specific solver/tool/scene mechanism?

---

### Template D — Build the state model / 提取状态机

**Coach / 教练**
- **中文**：这套流程通常先做什么，再做什么？什么时候从普通模式升级到更重的模式？
- **English**: What does this workflow do first, then next, and when does it escalate from a normal mode to a heavier one?

---

### Template E — Stop condition / 提取停止条件

**Coach / 教练**
- **中文**：什么时候可以有足够信心停止，不再继续迭代？
- **English**: When is there enough confidence to stop iterating?

---

### Template F — Human review / 提取人工复核机制

**Coach / 教练**
- **中文**：如果系统多轮都无法形成足够自信，何时要请人检查？请人检查后流程如何变化？
- **English**: If the system cannot reach enough confidence after multiple rounds, when should a human be asked to review, and how should the workflow change afterward?

---

### Template G — Reflection writeback / 提取反思写回

**Coach / 教练**
- **中文**：如果后续证明我们判断对了/错了，哪些经验要沉淀到长期记忆里？
- **English**: If later evidence proves the workflow right or wrong, what should be written into long-term memory?

---

## 9) Scenario-based coaching templates / 分场景训练模板

Use these scenario templates when a generic dialogue is not enough.

当通用提问不够时，使用这些分场景模板。

---

### Scenario 1 — Repeated investigation / 反复联查与定位类流程

**Best for / 适用**
- **中文**：多轮观察、定位、升级日志、人审复核的排查流程。
- **English**: Repeated investigation workflows with observation, escalation, deeper tracing, and human review.

**Coach should ask / 教练应重点问**
- **中文**：初始观察模式是什么？何时升级到重定位？何时请人审查？
- **English**: What is the initial observation mode? When does it escalate to deep tracing? When should human review be requested?

- **中文**：每轮必须保留哪些证据？图像、日志、结构化事件如何关联？
- **English**: What evidence must be preserved each round, and how are images, logs, and structured events linked?

**Freeze targets / 应冻结**
- state machine / 状态机
- escalation threshold / 升级阈值
- evidence schema / 证据结构
- human-review path / 人审路径

**Common mistake / 常见错误**
- **中文**：太早进入重日志，或只固化场景细节而没固化升级机制。
- **English**: Escalating to heavy logs too early, or freezing scene details without freezing the escalation logic.

---

### Scenario 2 — Review / QA / audit workflow / 评审、质检、审计流程

**Best for / 适用**
- **中文**：代码审查、材料核验、质量门禁、检查单执行。
- **English**: Code review, artifact verification, quality gates, and checklist-driven audits.

**Coach should ask / 教练应重点问**
- **中文**：检查项清单是什么？什么算 blocker，什么算 warning？
- **English**: What is the checklist, and what counts as a blocker versus a warning?

- **中文**：发现问题后需要什么级别的证据与定位精度？
- **English**: What level of evidence and localization is required for a finding?

**Freeze targets / 应冻结**
- review criteria / 评审标准
- severity model / 严重度模型
- reporting format / 报告格式

**Common mistake / 常见错误**
- **中文**：只有“觉得有问题”的经验，没有稳定的分级标准。
- **English**: Relying on intuition without a stable severity model.

---

### Scenario 3 — Reporting / deliverable workflow / 报告与交付物流程

**Best for / 适用**
- **中文**：周报、组会汇报、分析纪要、对外摘要、固定格式报告。
- **English**: Weekly reports, lab meeting summaries, analysis memos, external briefs, and repeatable deliverables.

**Coach should ask / 教练应重点问**
- **中文**：输出要包含哪些固定章节？什么必须简写，什么必须详细？
- **English**: Which sections are mandatory, and what must stay concise versus detailed?

- **中文**：输出面向谁？技术读者、管理者还是外部读者？
- **English**: Who is the audience—technical readers, managers, or external stakeholders?

**Freeze targets / 应冻结**
- section schema / 章节结构
- tone and depth / 语气与深度
- file/location policy / 文件与落点规则

**Common mistake / 常见错误**
- **中文**：只记住内容，不沉淀读者导向与格式导向规则。
- **English**: Capturing content but not audience and formatting rules.

---

### Scenario 4 — Automation / maintenance workflow / 自动化与维护流程

**Best for / 适用**
- **中文**：定时检查、监控、周期汇总、重复执行任务。
- **English**: Scheduled checks, monitoring, periodic summaries, and recurring operational tasks.

**Coach should ask / 教练应重点问**
- **中文**：任务多久运行一次？失败时要重试、报警，还是等待人工？
- **English**: How often does it run, and on failure should it retry, alert, or wait for a human?

- **中文**：什么情况下“无事可报”可以自动归档？
- **English**: Under what conditions can a “no findings” run be auto-archived?

**Freeze targets / 应冻结**
- scheduling rule / 调度规则
- success/no-findings policy / 成功与无发现策略
- failure handling / 失败处理

**Common mistake / 常见错误**
- **中文**：把调度信息和任务内容写混，导致自动化提示不自洽。
- **English**: Mixing scheduling details into the task prompt so the automation becomes inconsistent.

---

### Scenario 5 — Human-in-the-loop escalation / 人在回路中的升级流程

**Best for / 适用**
- **中文**：超过某阈值后请求人工检查，之后进入快速复核或反思回写。
- **English**: Workflows that escalate to human review after a threshold and then enter rapid verification or reflection.

**Coach should ask / 教练应重点问**
- **中文**：人工检查前系统要准备什么材料？人工反馈有哪些允许类型？
- **English**: What material must the system prepare before human review, and what feedback types are allowed?

- **中文**：人工反馈回来后，是继续执行、快速复核、还是只做总结反思？
- **English**: After human feedback, should the workflow continue execution, do a fast review, or only summarize and reflect?

**Freeze targets / 应冻结**
- escalation trigger / 升级触发器
- human evidence package / 人审材料包
- post-human state transition / 人审后状态迁移
- reflection sink / 反思写回落点

**Common mistake / 常见错误**
- **中文**：把人工审查看作终点，而不是学习闭环的一部分。
- **English**: Treating human review as the end rather than part of the learning loop.

---

### Scenario 6 — Knowledge/memory workflow / 知识沉淀与记忆更新流程

**Best for / 适用**
- **中文**：把规则写入 skill、solver memory、团队模板、知识库。
- **English**: Workflows that write rules into skills, solver memory, team templates, or knowledge bases.

**Coach should ask / 教练应重点问**
- **中文**：这条知识是通用流程规则、领域机制，还是一次性案例结论？
- **English**: Is this knowledge a generic workflow rule, a domain mechanism, or a one-off case result?

- **中文**：写入后未来会被谁复用？复用场景是什么？
- **English**: Who will reuse it later, and in what scenario?

**Freeze targets / 应冻结**
- memory ownership / 记忆归属
- writeback rule / 写回规则
- update trigger / 更新触发器

**Common mistake / 常见错误**
- **中文**：把临时状态写成长期规则，或把领域知识误写进通用 skill。
- **English**: Writing temporary state as durable memory, or putting domain knowledge into a generic skill.

---

## 10) Fill-in-the-blank prompt kit / 填空式提问模板

### Template 1 — Trigger
- **中文**：你是想把“___”这套做法长期固定下来，还是只修这一次？
- **English**: Do you want to permanently stabilize the process for “___”, or only fix this one run?

### Template 2 — Scope
- **中文**：这条规则适用于“___”所有类似任务，还是只适用于当前“___”？
- **English**: Should this rule apply to all future “___” tasks, or only to the current “___”?

### Template 3 — Escalation
- **中文**：当“___”发生多少次后，应该升级到“___”模式？
- **English**: After “___” happens how many times, should the workflow escalate into “___” mode?

### Template 4 — Stop
- **中文**：当达到“___”证据或“___”信心时，可以停止吗？
- **English**: Can the workflow stop once it reaches “___” evidence or “___” confidence?

### Template 5 — Human review
- **中文**：如果连续“___”轮仍未解决，是否申请人工检查？人工检查后进入“___”？
- **English**: If the workflow remains unresolved for “___” rounds, should it request human review, and after that enter “___”?

### Template 6 — Reflection
- **中文**：如果后续证明判断“___”，需要把哪条经验写入“___”？
- **English**: If later evidence proves the judgment was “___”, what lesson should be written into “___”?

---

## 11) Manual self-evolution rules / 手册自我进化规则

- **中文**：如果新的 workflow 训练会话暴露出更好的提问顺序，就更新本手册。
- **English**: If a new workflow-training session reveals a better questioning sequence, update this manual.

- **中文**：如果某类任务反复出现，就把它提炼成新的分场景模板。
- **English**: If a task category appears repeatedly, promote it into a new scenario template.

- **中文**：如果跨语言复用开始变重要，就同步维护双语解释，不只保留单语版本。
- **English**: If cross-language reuse becomes important, maintain paired bilingual guidance instead of a single-language version.

- **中文**：如果本手册某一部分开始重复“口头解释”，说明那部分该模板化了。
- **English**: If one part of the manual repeatedly requires verbal explanation, it probably needs a new template.

---

## 12) Final coaching reminder / 最后提醒

- **中文**：不要急着固化“答案”，先固化“得到答案的方法”。
- **English**: Do not rush to freeze the answer; freeze the method for getting the answer.

- **中文**：不要只固化当前领域的细节，更要固化状态机、升级条件、人审闭环、反思写回这些可迁移结构。
- **English**: Do not freeze only domain details; freeze the transferable structure: state model, escalation logic, human-review loop, and reflection writeback.
