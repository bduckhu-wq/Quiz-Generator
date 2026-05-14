# 相似题生成功能 - 总结文档

> **日期**：2026-05-12  
> **状态**：✅ 方案已确认，待启动开发

---

## 📋 功能概述

**功能名称**：原题截图举一反三  
**核心价值**：教师上传原题截图 → OCR 识别 → 生成 3 道相似题（70% 相似度）

**用户场景**：
- 课后作业补充
- 错题强化训练
- 考前刷题
- 分层教学

---

## ✅ 已确认的方案

### 1. OCR 识别方案

**✅ 最终选型**：**DeepSeek-V4 Vision API**

**理由**：
- 成本极低：$0.001/图（GPT-4V 的 1/7.5）
- 准确率满足 K12 场景：93%+（简单公式 98%）
- 中文识别优秀：国产模型，中文语义理解强
- 技术栈统一：已使用 DeepSeek 做题目生成
- 速度快：2-3 秒完成识别 + 参数提取

**成本对比**：
| 方案 | OCR 成本 | 月成本（1000次） |
|-----|---------|----------------|
| DeepSeek-V4 | $0.001 | $61 ⭐ |
| 通义千问-VL | $0.003 | $63 |
| GPT-4V | $0.0075 | $67.5 |
| Claude | $0.015 | $75 |
| 原方案 | $0.02 | $85 |

**节省 28% 成本**（$85 → $61）

详细对比：`docs/architecture/ocr-solution-comparison.md`

---

### 2. 功能范围

**✅ 固定参数（不可调整）**：
- 相似度：70%（中相似度）
- 生成数量：3 道
- 变化维度：按 Skill 规则自动执行
  - 核心层：0% 变化（知识点、模型、逻辑锁定）
  - 结构层：≤10% 变化（至少改 1 处）
  - 表达层：30-50% 变化（场景陌生化）
  - 数值层：80-100% 变化（大幅改变）

**✅ 用户可编辑**：
- OCR 识别结果（学科、年级、知识点等）
- 生成后的相似题（题目、选项、答案、解析）

---

### 3. 技术架构

**后端架构**：
```
FastAPI 路由
    ↓
SimilarQuestionAgent
    ↓
SimilarQuestionWorkflow (LangGraph)
    ├─ OCR 识别（DeepSeek-V4）
    ├─ 参数提取
    ├─ 生成相似题（调用 Skill）
    └─ 格式化输出
    ↓
返回 3 道相似题
```

**核心组件**：
1. `OCRService`：OCR 识别服务（DeepSeek-V4 Vision API）
2. `SimilarQuestionWorkflow`：LangGraph 流程图
3. `SimilarQuestionAgent`：Agent 实现
4. `similar-question-generation` Skill：从蜜蜂家校复制
5. FastAPI 路由：3 个接口
   - `/upload`：上传图片 + OCR 识别
   - `/generate`：生成相似题
   - `/generate/stream`：流式生成（SSE）

---

### 4. 开发计划

**阶段 1：后端开发（优先）**

| 任务 | 时长 |
|-----|------|
| 技术设计 + 环境准备 | 1 天 |
| OCR 服务 + 数据模型 | 2 天 |
| Workflow + Skill 集成 | 3 天 |
| FastAPI 路由 + 测试 | 2 天 |
| API 文档 + 部署 | 1 天 |
| **合计** | **9 天（约 2 周）** |

**验收标准**：
- ✅ 后端 API 可独立运行
- ✅ Postman 测试通过（上传图片 → 生成 3 道相似题）
- ✅ 单元测试覆盖率 ≥80%
- ✅ API 文档完整（Swagger UI 可访问）

**阶段 2：前端开发（后端验证通过后启动）**
- 时长：9 天（约 2 周）
- 内容：上传组件、预览界面、编辑功能、流式展示

**总时间线**：4 周

详细计划：`docs/planning/similar-question-backend-plan.md`

---

## 📄 生成的文档

### 产品文档
1. ✅ `docs/product/similar-question-feature-proposal.md`
   - 完整产品方案（32KB）
   - 功能设计、交互流程、MVP 范围、成本估算、风险分析

### 技术文档
2. ✅ `docs/architecture/ocr-solution-comparison.md`
   - OCR 方案详细对比（18KB）
   - DeepSeek-V4 vs GPT-4V vs Claude vs 通义千问-VL
   - 主流方案调研、实测数据、推荐理由

3. ✅ `docs/planning/similar-question-backend-plan.md`
   - 后端开发计划（21KB）
   - 详细任务清单（Day 1 ~ Day 9）
   - 代码示例、测试用例、验收标准

---

## 🚀 下一步行动

### 立即启动（确认后执行）

```bash
# 1. 创建开发分支
cd /Users/pinya_hu/Desktop/tare/AI_quiz_new
git checkout -b feature/similar-question-backend

# 2. 创建目录结构
mkdir -p backend/agents
mkdir -p backend/workflows/similar_question_workflow
mkdir -p backend/skills/similar-question-generation
mkdir -p backend/services
mkdir -p backend/tests/test_similar_question

# 3. 复制 Skill 文件
cp "/Users/pinya_hu/Desktop/tare SOLO beta/蜜蜂家校/similar-question-generation/SKILL.md" \
   backend/skills/similar-question-generation/

# 4. 安装依赖
pip install deepseek-sdk langgraph pydantic httpx pytest

# 5. 配置环境变量
echo "DEEPSEEK_API_KEY=sk-xxx" >> backend/.env

# 6. 开始编码
# 按照 docs/planning/similar-question-backend-plan.md 执行
```

### 开发流程

**Day 1：技术设计**
- [ ] 编写技术设计文档（`docs/architecture/similar-question-design.md`）
- [ ] 调研 DeepSeek-V4 Vision API
- [ ] 创建测试脚本验证 OCR 识别准确率

**Day 2-3：OCR 服务**
- [ ] 实现 `backend/services/ocr_service.py`
- [ ] 实现 `backend/models/similar_question.py`
- [ ] 编写单元测试

**Day 4-6：Workflow + Skill**
- [ ] 复制并调整 Skill 文件
- [ ] 实现 Workflow 流程图（graph.py、state.py、nodes.py）
- [ ] 实现 Agent（similar_question_agent.py）

**Day 7-8：API + 测试**
- [ ] 实现 FastAPI 路由（3 个接口）
- [ ] 编写集成测试
- [ ] Postman 测试验证

**Day 9：文档 + 部署**
- [ ] 编写 API 文档
- [ ] 更新 README
- [ ] 部署到测试环境
- [ ] 交付给前端团队

---

## 📊 预期效果

### 成本节省
- **单次生成成本**：$0.061（vs 原方案 $0.085）
- **月成本**（1000 次）：$61（vs 原方案 $85）
- **节省 28%**

### 功能指标
| 指标 | 目标值 |
|-----|--------|
| OCR 识别准确率 | ≥95% |
| 参数推断准确率 | ≥85% |
| 相似题生成成功率 | ≥98% |
| 单次生成耗时 | ≤20 秒 |
| 用户满意度 | ≥4.0/5.0 |

### 使用指标
| 指标 | 目标值 |
|-----|--------|
| 功能使用率 | ≥20% |
| 单题重新生成率 | ≤30% |
| 相似题加入试卷率 | ≥60% |
| 功能留存率 | ≥50% |

---

## 🎯 关键决策

### ✅ 已确认
1. OCR 识别使用 **DeepSeek-V4**（成本降低 95%）
2. 相似度固定 **70%**（不支持用户调整）
3. 生成数量固定 **3 道**（不支持自定义）
4. 变化维度固定按 **Skill 规则**（无勾选框）
5. **分阶段开发**：先后端（2 周）→ 后验证 → 再前端（2 周）

### ⏸️ 待后续讨论
- 是否支持多图上传（一次 3-5 张）
- 是否支持难度调整（生成更难/更简单的变体题）
- 是否保存到个人题库

---

## 📞 联系方式

**产品方案问题**：查看 `docs/product/similar-question-feature-proposal.md`  
**技术实现问题**：查看 `docs/planning/similar-question-backend-plan.md`  
**OCR 方案问题**：查看 `docs/architecture/ocr-solution-comparison.md`

---

**文档维护者**：产品团队 + 技术团队  
**最后更新**：2026-05-12  
**状态**：✅ 方案确认完成，等待启动开发指令
