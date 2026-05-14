---
name: prd-sync
description: 同步 PRD 文档变更到相关 Skill 和代码
---

# PRD 同步命令

当 PRD.md 发生变更时，使用此命令自动检查并同步到：

## 检查范围
1. **smart-question-generator/SKILL.md**
   - 参数分层规则（4.1 节）
   - 场景策略（5.2-5.4 节）
   - 题型枚举（8.3 节）

2. **后端 Agent 配置**（若已创建）
   - ExamAgent 的 system_prompt
   - AdaptAgent 的 system_prompt

3. **前端类型定义**（若已创建）
   - ExamResponse、Question、枚举类型（8.1-8.3 节）

## 执行步骤
1. 读取 PRD.md 的最新修改时间
2. 对比相关文件的修改时间
3. 若 PRD 更新 > 依赖文件更新时间，则：
   - 列出需要同步的章节
   - 提供同步建议
   - 询问是否执行自动同步

## 示例
```bash
# 触发同步检查
/prd-sync

# 输出示例：
# ⚠️ PRD.md 已更新（2026-04-27 22:30）
# 以下文件需要同步：
# - smart-question-generator/SKILL.md（最后更新：2026-04-27 19:49）
#   → 第 5.2 节"难度策略"已修改
# - backend/agents/exam_agent.py（未创建）
#   → 需根据新参数规则更新 system_prompt
#
# 是否执行自动同步？[y/N]
```
