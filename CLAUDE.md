# AI 出题助手 - 项目指南

> 版本：v1.0 | 日期：2026-04-27
> 本文档为 Claude Code 提供项目上下文和协作准则

---

## 📋 项目概述

**产品名称**：AI 出题助手  
**产品定位**：面向 K12 教师的轻量级 AI 智能出题系统 demo  
**核心场景**：通过多轮对话梳理出题需求，自动生成结构化试卷并支持预览和导出

**技术栈预期**：
- 前端：React/Next.js（待确认）
- 后端：FastAPI（Python）
- AI 能力：LLM Tool Calling（支持 Kimi/DeepSeek/Claude/通义千问）
- Agent 框架：Claude Agent SDK（含 Skill 机制）

---

## 🎯 核心功能模块

### 1. 多轮对话出题流程
- 自然语言输入需求 → AI 参数提取 → 追问补全 → 参数确认面板
- 参数分层：核心身份（学科/年级）、内容入口（教材章节 或 知识点）、场景策略（难度/题型/题量）
- 双入口机制：路径A（教材版本+章节）、路径B（知识点自由输入）

### 2. Agent 智能调度
- **ExamAgent**（出题 Agent）：负责参数提取、试卷蓝图设计、调用 `generate_exam` 工具
- **AdaptAgent**（改编 Agent）：负责单题改编（提难度/降难度/换题型/换考点）
- Agent 实时思考过程展示（SSE 流式输出）

### 3. 试卷预览与编辑
- 左右分栏布局（对话历史 + 试卷预览）
- 支持题目增删、拖拽排序、重新生成、单题改编
- 导出 Word 格式试卷（含/不含答案切换）

### 4. 场景策略系统
- 4 种出题场景：课后作业、单元测验、期中期末考试、考前复习
- 每种场景对应不同的难度分布、题型分布、题量范围
- AI 自动推断场景或由用户指定

---

## 📁 项目结构

```
AI_quiz_new/
├── README.md                      # 项目概述与文档导航
├── CLAUDE.md                      # 本文档（项目指南）
├── start.sh / stop.sh             # 启动/停止脚本
│
├── docs/                          # 📚 文档中心
│   ├── product/                   # 产品文档
│   │   ├── PRD.md                 # 产品需求文档
│   │   ├── interaction-design.md  # 交互设计
│   │   └── parameter-rules.md     # 参数规则
│   ├── architecture/              # 架构文档
│   │   ├── overview.md            # 架构概览
│   │   ├── data-model.md          # 数据模型
│   │   └── tech-stack.md          # 技术栈
│   ├── guides/                    # 操作指南
│   │   ├── getting-started.md     # 启动指南
│   │   └── frontend-development.md # 前端开发指南
│   ├── reference/                 # 参考文档
│   │   ├── api-spec.md            # API 规范
│   │   ├── chat-components.md     # 对话组件
│   │   ├── decision-log.md        # 决策记录
│   │   └── development.md         # 开发规范
│   ├── planning/                  # 规划文档
│   │   ├── ROADMAP.md             # 路线图
│   │   └── CHANGELOG.md           # 变更记录
│   └── archive/                   # 历史归档
│
├── backend/                       # 🐍 后端服务
│   ├── agents/                    # Agent 实现
│   ├── skills/                    # Skill 配置
│   ├── workflows/                 # LangGraph 工作流
│   ├── tools/                     # Agent 工具
│   ├── services/                  # 业务服务
│   ├── models/                    # 数据模型
│   └── app/                       # FastAPI 应用
│
├── frontend/                      # ⚛️ 前端应用
│   ├── app/                       # Next.js 页面
│   ├── components/                # React 组件
│   └── hooks/                     # 自定义 Hooks
│
├── smart-question-generator/      # 📝 出题 Skill 子项目
│   └── SKILL.md                   # Skill 定义
│
└── .claude/                       # Claude Code 配置
    ├── settings.json              # 项目设置
    ├── skills/                    # 本地 Skill
    └── rules/                     # 代码规范
```

**重要文件说明**：
- **docs/product/PRD.md**：完整的产品需求文档，涵盖用户流程、参数规则、场景策略、API 设计、MVP 范围
- **docs/product/interaction-design.md**：详细的交互设计文档，包含页面布局、交互流程、组件规范
- **docs/product/parameter-rules.md**：参数规则详解，包含参数分层、场景策略、追问规则
- **docs/architecture/overview.md**：技术架构概览，Skill + Workflow 融合设计
- **smart-question-generator/SKILL.md**：出题规则 Skill，包含参数分层、18种题型、场景策略等核心逻辑

---

## 🤝 协作准则

### 1. 产品导向思维
- **始终参考 PRD**：任何功能开发、需求澄清、技术选型均需对齐 `docs/product/PRD.md` 中的定义
- **用户视角优先**：所有功能设计从"老师使用场景"出发，避免技术优先
- **参数完整性校验**：严格遵守 `docs/product/parameter-rules.md` 中的"参数满足判定"规则（学科 + 年级 + 内容入口 = 最低门槛）

### 2. 文档更新规范
- **PRD 修改**：涉及需求变更时，必须先更新 `docs/product/PRD.md` 对应章节，标注版本和修改说明
- **Skill 文档同步**：若参数规则、场景策略变化，同步更新 `smart-question-generator/SKILL.md`
- **决策记录**：重要技术选型、架构调整需在 `docs/reference/decision-log.md` 记录

### 3. 文档最小化原则（重要 ⚠️）

**核心原则**：能合并就合并，能删除就删除，避免过度文档化

**分层规范**：
- **产品层**：1 个 PRD（做什么、为什么）
- **规划层**：1 个开发计划（怎么做、什么时候）
- **参考层**：仅在必要时创建（技术细节、API 文档）

**禁止行为**：
- ❌ 创建多个总结文档（如 SUMMARY.md、OVERVIEW.md、INTRO.md 重复）
- ❌ 将同一内容拆分成多个文档（如方案对比单独成文）
- ❌ 创建临时性文档后不归档（如更新说明、调研报告）
- ❌ 在 PRD 中放置详细代码示例（应在开发计划中）

**文档生命周期**：
1. **研究阶段**：可创建临时文档（如方案对比、技术调研）
2. **决策完成**：将核心结论合并到正式文档（PRD、开发计划）
3. **立即归档**：临时文档移入 `docs/archive/项目名-日期/`，添加 README 说明

**归档规范**：
```bash
# 归档目录命名
docs/archive/功能名-研究-YYYYMMDD/

# 必须包含 README.md 说明
- 归档时间
- 归档原因
- 核心结论（已合并到哪个正式文档）
- 正式文档链接
```

**检查清单**（每次生成文档后）：
- [ ] 是否与现有文档重复？→ 合并
- [ ] 是否为临时性文档？→ 用完即归档
- [ ] 是否包含过多技术细节？→ 移到开发计划
- [ ] 文档数量是否 >3 个？→ 重新审视必要性

**反面案例**（本项目曾犯的错误）：
- 相似题功能初期生成了 6 个文档（100KB+），实际只需 2 个核心文档（25KB）
- `ocr-solution-comparison.md`（18KB）单独成文，实际只需在 PRD 中 1 段话说明结论
- `SUMMARY.md` 与 PRD 内容重复 80%
- 临时更新说明文档（`V3_TO_V4_UPDATE.md`）未及时删除

**正面案例**：
- 产品方案：1 个 PRD（15KB，包含需求、流程、成本、风险）
- 开发计划：1 个 dev-plan（10KB，包含任务清单、核心代码、验收标准）
- 归档研究文档：4 个（46KB，仅供历史查阅，不维护）

### 3. 代码规范（待完善）
- **后端**：
  - Agent 配置统一在 `skills/` 目录管理
  - Tool 定义遵循 Claude Agent SDK 规范
  - 会话管理使用 SessionMemory（JSON 文件存储）
  - 日志记录到 `logs/agent_YYYYMMDD.log`
- **前端**：
  - 数学公式使用 KaTeX 渲染
  - 题目拖拽使用 @dnd-kit/core
  - SSE 流式输出使用 ReadableStream + TextDecoder
  - 参数面板交互遵循 PRD 6.3 节设计

### 4. 提问与澄清
当遇到以下情况时，应主动提问而非臆测：
- PRD 中未明确定义的边界条件（如"用户输入空字符串时如何处理？"）
- 多个方案可选时的优先级（如"题目 ID 使用 UUID 还是自增 ID？"）
- 跨模块交互的数据格式（如"前端传递给后端的参数面板 JSON 格式是？"）

### 5. AI 功能设计特殊要求
- **所有 AI 生成内容必须可人工修改**：题目、答案、解析均支持编辑
- **AI 能力不夸大**：生成的题目需明确标注"AI 生成，仅供参考"
- **隐私保护**：不处理学生个人信息，仅服务教师出题场景
- **符合教育合规**：避免不当内容（暴力、色情、歧视）进入题库

---

## 🚀 快速开始（开发者）

### 环境要求
- Python 3.9+（后端）
- Node.js 16+（前端，若使用）
- LLM API Key（Kimi/DeepSeek/Claude/通义千问 任一）

### 运行流程（MVP 阶段）
1. **后端启动**：
   ```bash
   cd backend  # 目录待创建
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **前端启动**：
   ```bash
   cd frontend  # 目录待创建
   npm install
   npm run dev
   ```

3. **访问**：http://localhost:3000

### 测试场景（Checklist）
- [ ] 用户输入"帮我出一份初二数学期末试卷" → AI 追问补全 → 生成试卷
- [ ] 参数面板滑块调整难度/题量 → 确认生成 → 试卷分栏预览
- [ ] 单题改编（提难度）→ 题目内容更新
- [ ] 拖拽排序 → 题号自动更新
- [ ] 导出 Word → 下载 .docx 文件

---

## 🔐 安全与合规

### 数据隐私
- **会话数据**：存储在本地 `sessions/` 目录，不上传云端
- **题目数据**：生成后存储在 `exams/` 目录（JSON 格式），可选择性清理
- **敏感信息**：不记录教师个人身份信息（如真实姓名、学校）

### AI 内容审核
- **题目合规性**：生成后自动检查是否包含违规关键词（暴力、色情、政治敏感）
- **答案准确性**：AI 生成的答案仅作为参考，需教师人工审核确认
- **知识点匹配**：知识点库基于教育部课程标准，定期更新

---

## 📌 关键决策记录

### 决策 1：Agent 选择机制采用硬编码路由而非 AI 决策
**时间**：2026-04-27  
**背景**：PRD 7.1 节原设计让 LeadAgent 自主决策调用哪个 Agent  
**决策**：改为 FastAPI 路由层硬编码分发（`/api/exam/generate` → ExamAgent、`/api/exam/adapt` → AdaptAgent）  
**原因**：
- 出题和改编是明确的业务路径，无需 AI 判断
- 避免 Agent 选择错误导致的额外调试成本
- 降低 token 消耗（无需额外的决策轮次）

### 决策 2：会话管理使用 JSON 文件而非数据库
**时间**：2026-04-27  
**背景**：MVP 阶段需快速验证产品逻辑  
**决策**：使用 JSON 文件存储会话（`sessions/{session_id}.json`）  
**原因**：
- 无需引入数据库依赖，简化部署
- 会话数据量小（每个会话约 1-5KB），文件读写性能足够
- 后续可平滑迁移至 Redis/PostgreSQL

**迁移计划**：若单用户会话数 > 100 或并发用户 > 10，则迁移至 Redis

### 决策 3：参数面板采用"统一展示"而非"分段确认"
**时间**：2026-04-27  
**背景**：PRD 3.1 节参数确认面板设计  
**决策**：所有参数（已确认 + AI 推断）统一在参数面板展示，不区分视觉样式  
**原因**：
- 避免"已确认"和"AI 默认"的视觉区分导致认知负担
- 教师可自由修改任何参数，无需关心来源
- 简化前端逻辑（无需维护参数状态标记）

---

## 🛠️ 待办事项（项目级）

### 立即处理
- [ ] 创建后端目录结构（`backend/`、`backend/agents/`、`backend/tools/`、`backend/sessions/`）
- [ ] 创建前端目录结构（`frontend/src/pages/`、`frontend/src/components/`）
- [ ] 编写 ExamAgent 的 System Prompt（基于 PRD + smart-question-generator/SKILL.md）
- [ ] 实现 `generate_exam` 工具（调用 LLM 生成题目数组）

### 近期规划
- [ ] 完成首页 + 对话页前端布局
- [ ] 实现 SSE 流式输出（后端 FastAPI + 前端 ReadableStream）
- [ ] 完成参数面板组件（滑块 + 下拉框 + 文本框）
- [ ] 实现试卷预览分栏布局

### 长期优化
- [ ] 支持 LaTeX 公式渲染
- [ ] 增加题目收藏功能
- [ ] 接入知识图谱可视化
- [ ] 多人协作出题

---

## 📚 参考资源

### 内部文档
- **docs/product/PRD.md**：完整产品需求文档
- **docs/product/interaction-design.md**：详细交互设计
- **docs/product/parameter-rules.md**：参数规则详解
- **docs/architecture/overview.md**：技术架构概览
- **docs/reference/api-spec.md**：API 规范
- **smart-question-generator/SKILL.md**：出题规则 Skill
- **~/.claude/CLAUDE.md**：全局产品经理工作准则（用户私有配置）

### 技术文档
- [Claude Agent SDK 文档](https://docs.anthropic.com/claude-agent-sdk)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Server-Sent Events (SSE) 规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### 教育资源
- 教育部课程标准：http://www.moe.gov.cn/
- K12 学科知识点体系（待补充）

---

## 🎉 版本记录

### v1.0 (2026-04-27)
- 初始化项目配置
- 创建 CLAUDE.md 指南
- 确定 Agent 架构（ExamAgent + AdaptAgent）
- 明确参数分层规则和场景策略

---

**提示**：本文档是 Claude Code 的主要协作入口，任何影响产品逻辑、技术架构的变更均需在此记录。
