# 📚 AI出题助手 - 文档中心

> **文档版本**：v2.0 | **更新日期**：2026-05-12

---

## 📖 文档导航

### 🚀 快速开始（新手必读）

1. [**启动指南**](guides/getting-started.md) ⭐ - 环境配置、一键启动、常见问题
2. [前端开发指南](guides/frontend-development.md) - 前端项目结构、组件开发

---

### 📋 产品设计（产品经理、设计师）

- [**产品需求文档 (PRD)**](product/PRD.md) - 产品定位、核心功能、MVP 范围
- [交互设计](product/interaction-design.md) - 页面设计、交互流程、组件规范（31KB，650行）
- [参数规则](product/parameter-rules.md) - 参数分层、场景策略、追问规则（10KB，380行）

**阅读顺序**：PRD → 参数规则 → 交互设计

---

### 🏗️ 技术架构（后端开发、架构师）

- [**架构概览**](architecture/overview.md) ⭐ - Skill + Workflow 融合架构、Agent 调度
- [数据模型](architecture/data-model.md) - Question、Exam、Session 数据结构
- [技术栈](architecture/tech-stack.md) - 前后端技术选型、LLM 提供商

**阅读顺序**：架构概览 → 数据模型 → 技术栈

**补充阅读**：
- [backend/SKILL_ARCHITECTURE.md](../backend/SKILL_ARCHITECTURE.md) - Skill 架构详解
- [backend/WORKFLOW_DIAGRAM.md](../backend/WORKFLOW_DIAGRAM.md) - 工作流程图

---

### 📖 开发参考（前后端开发）

#### API 与接口
- [API 规范](reference/api-spec.md) - 接口定义、请求响应格式、错误码

#### 组件与模块
- [对话组件](reference/chat-components.md) - 对话界面组件详解（24KB）
- [开发规范](reference/development.md) - 代码规范、开发流程

#### 决策与规则
- [决策记录 (ADR)](reference/decision-log.md) - 架构决策记录（4条）
- [决策树](reference/decision-tree.md) - 场景识别、参数提取决策可视化
- [内容决策流](reference/content-decision-flow.md) - 内容入口选择逻辑

---

### 📅 项目管理（项目经理、团队）

- [路线图](planning/ROADMAP.md) - 迭代计划、功能排期
- [变更记录](planning/CHANGELOG.md) - 版本历史、更新日志

---

### 📦 历史归档

以下文档为历史版本或临时文档，仅供参考：

- [文档拆分总结](archive/DOCUMENT_SPLIT_SUMMARY.md) - PRD v5.0 拆分报告（2026-04-28）
- [PRD v5.0 备份](archive/PRD_v5.0_backup.md) - 旧版 PRD（1200行，已废弃）
- [PRD Demo 版](archive/PRD_demo.md) - 演示版 PRD（已废弃）
- [项目总结](archive/PROJECT_SUMMARY.md) - 早期项目总结
- [测试报告](archive/test-report-20260428.md) - 2026-04-28 测试快照
- [UI 优化建议](archive/ui-optimization-ideas.md) - UI/UX 优化想法（已部分实现）
- [部署草稿](archive/deployment-draft.md) - 部署指南草稿（待补充）

---

## 📂 文档结构说明

```
docs/
├── README.md              # 本文档（文档导航）
│
├── product/               # 产品文档（产品经理、设计师）
│   ├── PRD.md             # 产品需求文档（核心）
│   ├── interaction-design.md  # 交互设计（详细）
│   └── parameter-rules.md     # 参数规则（教研友好）
│
├── architecture/          # 架构文档（后端开发、架构师）
│   ├── overview.md        # 架构概览（框架，待补充）
│   ├── data-model.md      # 数据模型（框架，待补充）
│   └── tech-stack.md      # 技术栈（框架，待补充）
│
├── guides/                # 操作指南（所有开发者）
│   ├── getting-started.md     # 启动指南（必读）
│   └── frontend-development.md # 前端开发指南
│
├── reference/             # 参考文档（开发过程查阅）
│   ├── api-spec.md        # API 规范（框架，待补充）
│   ├── chat-components.md # 对话组件详解
│   ├── decision-log.md    # 决策记录（持续更新）
│   ├── decision-tree.md   # 决策树可视化
│   ├── content-decision-flow.md # 内容决策流
│   └── development.md     # 开发规范
│
├── planning/              # 规划文档（项目管理）
│   ├── ROADMAP.md         # 路线图（持续更新）
│   └── CHANGELOG.md       # 变更记录（持续更新）
│
└── archive/               # 历史归档（仅供参考）
    ├── DOCUMENT_SPLIT_SUMMARY.md
    ├── PRD_v5.0_backup.md
    ├── PRD_demo.md
    ├── PROJECT_SUMMARY.md
    ├── test-report-20260428.md
    ├── ui-optimization-ideas.md
    └── deployment-draft.md
```

---

## 🎯 文档使用指南

### 按角色查找

| 角色 | 必读文档 | 参考文档 |
|-----|---------|---------|
| **产品经理** | PRD、交互设计、参数规则 | 决策记录、路线图 |
| **设计师** | 交互设计 | PRD、对话组件 |
| **前端开发** | 启动指南、前端开发指南、交互设计 | API规范、对话组件、开发规范 |
| **后端开发** | 启动指南、架构概览、参数规则 | API规范、数据模型、开发规范 |
| **教研人员** | 参数规则 | PRD、决策树 |
| **项目经理** | PRD、路线图、变更记录 | 决策记录 |

### 按场景查找

| 场景 | 推荐文档 |
|-----|---------|
| **首次接触项目** | 启动指南 → PRD → 架构概览 |
| **开发新功能** | PRD → 参数规则 → 交互设计 → API规范 |
| **理解参数逻辑** | 参数规则 → 决策树 → 内容决策流 |
| **前端界面开发** | 交互设计 → 对话组件 → 前端开发指南 |
| **后端 Agent 开发** | 架构概览 → backend/SKILL_ARCHITECTURE.md |
| **调整场景策略** | 参数规则 → smart-question-generator/SKILL.md |
| **排查问题** | 决策记录 → 开发规范 → 启动指南常见问题 |

---

## 📝 文档维护规范

### 更新频率

| 文档类型 | 更新频率 | 触发条件 |
|---------|---------|---------|
| **产品文档** | 低 | 功能级迭代、需求变更 |
| **架构文档** | 低-中 | 技术架构调整、重大重构 |
| **操作指南** | 中 | 部署流程变化、工具升级 |
| **参考文档** | 中-高 | 接口变更、组件更新 |
| **规划文档** | 高 | 每次发布、里程碑完成 |

### 更新流程

1. **产品需求变更**
   - 更新 `product/PRD.md` 对应章节
   - 同步更新 `product/interaction-design.md`（如涉及交互）
   - 同步更新 `product/parameter-rules.md`（如涉及参数）
   - 记录决策到 `reference/decision-log.md`（如有重大决策）

2. **技术架构调整**
   - 更新 `architecture/overview.md`
   - 同步更新 `architecture/data-model.md`（如涉及数据结构）
   - 记录决策到 `reference/decision-log.md`

3. **版本发布**
   - 更新 `planning/CHANGELOG.md`
   - 更新 `planning/ROADMAP.md`（标记完成项）

---

## 🔄 文档历史

### v2.0 (2026-05-12)
- ✅ 重组文档结构，按职责分类
- ✅ 根目录文档从 8 个减至 2 个
- ✅ 创建 6 个分类目录（product / architecture / guides / reference / planning / archive）
- ✅ 更新 README.md 添加完整文档导航
- ✅ 创建 docs/README.md 文档中心索引

### v1.0 (2026-04-28)
- ✅ 拆分 PRD v5.0 为 12 个独立文档
- ✅ 核心 PRD 从 1200 行精简至 300 行
- ✅ 创建交互设计、参数规则等专项文档

---

## 💡 帮助与反馈

- **找不到文档？** 使用 `grep` 搜索：`grep -r "关键词" docs/`
- **文档过时？** 提交 Issue 或直接更新文档并记录变更
- **建议改进？** 联系项目负责人或在 planning/ROADMAP.md 添加建议

---

**文档维护者**：产品团队 + 技术团队  
**最后更新**：2026-05-12
