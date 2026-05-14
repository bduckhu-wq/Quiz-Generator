# 🎓 AI出题助手

> **智能对话生成高质量试卷系统**  
> 版本 v1.0 | 2026-05-12

---

## 🌐 在线体验

📍 **部署地址即将更新**

前端部署：[![Vercel](https://img.shields.io/badge/Vercel-部署中-blue)](https://vercel.com)  
后端部署：[![Railway](https://img.shields.io/badge/Railway-部署中-purple)](https://railway.app)

详细部署步骤见 **[DEPLOYMENT.md](./DEPLOYMENT.md)**

---

## 🚀 本地开发

```bash
cd /Users/pinya_hu/Desktop/tare/AI_quiz_new
./start.sh
```

然后访问：**http://localhost:3000**

停止服务：`./stop.sh`

---

## ✨ 核心特性

- 🤖 **智能理解**：自然语言输入，AI自动识别需求
- 🔄 **多轮对话**：参数不完整时智能追问补全
- ⚡ **实时反馈**：SSE流式输出，实时查看生成进度
- 📊 **混合出题**：题库检索 + AI生成补充
- 💾 **会话持久化**：刷新页面保持对话状态
- 📝 **即时预览**：双栏布局，左侧对话右侧试卷

---

## 📊 系统数据

- **总题目数**：160道（三年级60道 + 初二100道）
- **支持年级**：小学1-6年级 + 初中1-3年级 + 高中1-3年级
- **题型**：18种
- **性能**：参数提取1-2秒 + 题库搜索0.02秒 + AI生成10-25秒

---

## 💡 使用示例

```
输入: "三年级数学第三章第二节课后练习5题"
  ↓ (15秒)
输出: ✅ 试卷已生成完成！5道题，40分
```

---

## 📚 完整文档导航

### 🚀 快速开始
- [**启动指南**](docs/guides/getting-started.md) ⭐ **必读** - 一键启动、环境配置、常见问题
- [前端开发指南](docs/guides/frontend-development.md) - 前端项目结构、组件说明、开发流程

### 📋 产品设计
- [**产品需求文档 (PRD)**](docs/product/PRD.md) - 产品定位、核心功能、用户流程
- [交互设计](docs/product/interaction-design.md) - 详细页面设计、交互流程、组件规范
- [参数规则](docs/product/parameter-rules.md) - 参数分层、场景策略、追问规则

### 🏗️ 技术架构
- [**架构概览**](docs/architecture/overview.md) ⭐ **推荐** - Skill + Workflow 融合架构
- [数据模型](docs/architecture/data-model.md) - Question、Exam、Session 数据结构
- [技术栈](docs/architecture/tech-stack.md) - 前后端技术选型

### 📖 开发参考
- [API 规范](docs/reference/api-spec.md) - 接口定义、请求响应格式
- [对话组件](docs/reference/chat-components.md) - 对话界面组件详解
- [决策记录](docs/reference/decision-log.md) - 架构决策记录 (ADR)
- [决策树](docs/reference/decision-tree.md) - 场景识别、参数提取决策可视化
- [内容决策流](docs/reference/content-decision-flow.md) - 内容入口选择逻辑
- [开发规范](docs/reference/development.md) - 代码规范、开发流程

### 📅 项目管理
- [路线图](docs/planning/ROADMAP.md) - 迭代计划、功能排期
- [变更记录](docs/planning/CHANGELOG.md) - 版本历史、更新日志

### 📦 历史归档
- [归档文档](docs/archive/) - 旧版本文档、测试报告等

---

## 🏗️ 项目结构

```
AI_quiz_new/
├── README.md              # 本文档
├── CLAUDE.md              # Claude Code 项目指南
├── start.sh / stop.sh     # 启动/停止脚本
│
├── docs/                  # 📚 文档目录
│   ├── product/           # 产品文档（PRD、交互设计）
│   ├── architecture/      # 架构文档（系统设计、数据模型）
│   ├── guides/           # 操作指南（启动、开发、部署）
│   ├── reference/        # 参考文档（API、组件、决策记录）
│   ├── planning/         # 规划文档（路线图、变更记录）
│   └── archive/          # 历史归档
│
├── backend/              # 🐍 后端服务
│   ├── agents/           # Agent 实现（ExamAgent、AdaptAgent）
│   ├── skills/           # Skill 配置（教研可编辑）
│   ├── workflows/        # LangGraph 工作流
│   ├── tools/            # Agent 工具（generate_exam、adapt_question）
│   ├── services/         # 业务服务（题库搜索、LLM调用）
│   ├── models/           # 数据模型（Question、Exam、Session）
│   └── app/              # FastAPI 应用
│
├── frontend/             # ⚛️ 前端应用
│   ├── app/              # Next.js 页面
│   ├── components/       # React 组件
│   ├── hooks/            # 自定义 Hooks
│   └── lib/              # 工具库
│
└── smart-question-generator/  # 📝 出题 Skill 子项目
    └── SKILL.md          # Skill 定义（参数规则、题型、场景策略）
```

---

## 🔧 技术栈

- **前端**：Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **后端**：FastAPI + Python 3.9 + LangGraph + Claude Agent SDK
- **AI**：支持 Kimi/DeepSeek/Claude/通义千问
- **数据**：SQLite（题库） + JSON（会话）

---

## 📖 相关文档

### 后端专属
- [backend/DELIVERY.md](backend/DELIVERY.md) - 后端交付文档
- [backend/PROJECT_STRUCTURE.md](backend/PROJECT_STRUCTURE.md) - 后端项目结构详解
- [backend/SKILL_ARCHITECTURE.md](backend/SKILL_ARCHITECTURE.md) - Skill 架构设计
- [backend/WORKFLOW_DIAGRAM.md](backend/WORKFLOW_DIAGRAM.md) - 工作流程图

### Skill 配置
- [smart-question-generator/SKILL.md](smart-question-generator/SKILL.md) - 出题规则 Skill 定义

---

## 🎯 当前状态

**✅ v1.0 已完成，可立即使用！**

- ✅ 多轮对话参数提取
- ✅ 题库检索 + AI 补充
- ✅ 实时流式输出
- ✅ 试卷预览与导出
- ✅ 会话持久化

---

## 📞 帮助与反馈

- **快速上手**：先阅读 [启动指南](docs/guides/getting-started.md)
- **开发问题**：参考 [开发规范](docs/reference/development.md)
- **架构理解**：查看 [架构概览](docs/architecture/overview.md)
- **功能建议**：提交到 [路线图](docs/planning/ROADMAP.md)

---

**最后更新**：2026-05-12 | **文档版本**：v2.0
