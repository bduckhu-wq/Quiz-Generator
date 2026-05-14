# AI 出题助手 - 技术架构文档

> **版本**：v1.0 | **日期**：2026-04-28

---

## 1. 整体架构

```
前端 → FastAPI → MainAgent → Skill → Workflow → Services → 数据层
```

---

## 2. Skill + Workflow 融合模式

**Skill（策略层）**：
- 配置文件：`config.yaml`
- 教研人员可编辑
- 定义场景策略、参数规则

**Workflow（执行层）**：
- LangGraph 流程图
- 开发人员维护
- 保证执行稳定性

---

## 3. ExamWorkflow 流程图

```
开始 → 提取参数 → 检查完整性 → 匹配场景 → 搜题 → AI补充 → 组卷 → 结束
```

---

详细架构设计参见 `backend/SKILL_ARCHITECTURE.md`。

**文档维护者**：架构团队  
**最后更新**：2026-04-28
