# 相似题生成 Workflow

> **技术架构**：LangGraph  
> **创建日期**：2026-05-12  
> **负责人**：后端团队

---

## 📋 功能概述

基于原题截图生成 3 道相似题，保持核心知识点不变，变化表层维度（场景、数值、表述）。

**核心流程**：
```
上传图片 → OCR识别+参数推断 → 生成3道相似题 → 有效性校验 → 返回结果
```

---

## 🏗️ Workflow 架构

### 节点定义

| 节点名称 | 功能 | 输入 | 输出 |
|---------|------|------|------|
| `ocr_recognize_and_infer_params` | OCR 识别 + 参数推断 | 图片路径 | OCR 结果（含参数） |
| `generate_similar` | 生成相似题 | OCR 结果 | 3 道相似题 |
| `validate_questions` | 有效性校验 | 相似题列表 | 校验结果 |
| `format_output` | 格式化输出 | 相似题 + 校验结果 | 最终 JSON |

### 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    SimilarQuestionWorkflow                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ocr_recognize_and_infer_params                      │   │
│  │  - 调用 DeepSeek V4 Vision API                       │   │
│  │  - 识别题目内容                                       │   │
│  │  - 推断学科/年级/知识点/题型/难度                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ↓                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  generate_similar                                    │   │
│  │  - 调用 similar-question-generation Skill            │   │
│  │  - 基于 OCR 结果生成 3 道相似题                      │   │
│  │  - 相似度固定 70%                                    │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ↓                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  validate_questions                                  │   │
│  │  - 并行校验 3 道题的有效性                           │   │
│  │  - 检查条件充分性、逻辑一致性、答案唯一性             │   │
│  │  - 失败题目自动重新生成（最多重试 2 次）              │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ↓                                         │
│            校验是否全部通过？                                 │
│                     ├─ 是 ──────────┐                        │
│                     └─ 否（重试）    │                        │
│                           ↓          ↓                        │
│                    retry_count < 2 ? │                        │
│                           ├─ 是 ─────┤                        │
│                           │          │                        │
│                    重新生成失败的题   │                        │
│                           │          │                        │
│                           ↓          ↓                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  format_output                                       │   │
│  │  - 格式化为标准 JSON                                  │   │
│  │  - 添加元数据（生成时长、校验结果）                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 状态定义

```python
class SimilarQuestionWorkflowState(TypedDict):
    # 输入
    image_url: str                      # 图片路径
    
    # 中间状态
    ocr_result: dict                    # OCR 识别结果（含参数推断）
    original_question: dict             # 原题结构化数据
    similar_questions: list[dict]       # 生成的相似题列表
    validation_results: list[dict]      # 有效性校验结果
    retry_count: int                    # 重试次数（0-2）
    
    # 输出
    error: str | None                   # 错误信息
```

**字段说明**：
- `image_url`：输入的原题图片路径
- `ocr_result`：OCR 识别结果，包含：
  - `question`：题目内容
  - `subject`：学科
  - `grade`：年级
  - `knowledge_point`：知识点
  - `question_type`：题型
  - `difficulty`：难度
  - `confidence`：识别置信度
- `similar_questions`：生成的 3 道相似题，每道题包含：
  - `id`：题目 ID
  - `question`：题目内容
  - `options`：选项（如有）
  - `answer`：答案
  - `explanation`：解析
  - `metadata`：元数据（学科、知识点等）
- `validation_results`：校验结果，每道题包含：
  - `valid`：是否有效（true/false）
  - `reason`：原因（如果无效）

---

## 🔧 技术实现

### 依赖

```bash
pip install langgraph openai pydantic python-dotenv
```

### 核心代码

**graph.py**：定义 Workflow 流程

```python
from langgraph.graph import StateGraph, END
from .state import SimilarQuestionWorkflowState
from . import nodes

def create_similar_question_workflow():
    """创建相似题生成 Workflow"""
    workflow = StateGraph(SimilarQuestionWorkflowState)
    
    # 添加节点
    workflow.add_node("ocr_recognize", nodes.ocr_recognize_and_infer_params)
    workflow.add_node("generate_similar", nodes.generate_similar)
    workflow.add_node("validate_questions", nodes.validate_questions)
    workflow.add_node("format_output", nodes.format_output)
    
    # 设置流程
    workflow.set_entry_point("ocr_recognize")
    workflow.add_edge("ocr_recognize", "generate_similar")
    workflow.add_edge("generate_similar", "validate_questions")
    
    # 校验失败重试逻辑
    def should_retry(state):
        """判断是否需要重试"""
        failed_count = sum(1 for r in state["validation_results"] if not r["valid"])
        return "generate_similar" if failed_count > 0 and state["retry_count"] < 2 else "format_output"
    
    workflow.add_conditional_edges("validate_questions", should_retry)
    workflow.add_edge("format_output", END)
    
    return workflow.compile()
```

**nodes.py**：实现各节点逻辑

```python
async def ocr_recognize_and_infer_params(state: SimilarQuestionWorkflowState):
    """OCR 识别 + 参数推断节点"""
    from services.ocr_service import OCRService
    
    ocr_service = OCRService()
    ocr_result = await ocr_service.recognize_question(state["image_url"])
    
    return {
        "ocr_result": ocr_result,
        "original_question": {
            "question": ocr_result["question"],
            "subject": ocr_result["subject"],
            "grade": ocr_result["grade"],
            "knowledge_point": ocr_result["knowledge_point"]
        }
    }

async def generate_similar(state: SimilarQuestionWorkflowState):
    """生成相似题节点"""
    from services.llm_service import LLMService
    
    # 调用 similar-question-generation Skill
    # TODO: 实现 Skill 调用逻辑
    
    return {"similar_questions": [...]}

async def validate_questions(state: SimilarQuestionWorkflowState):
    """有效性校验节点"""
    from services.llm_service import LLMService
    
    # 并行校验 3 道题
    # TODO: 实现校验逻辑
    
    return {"validation_results": [...]}

async def format_output(state: SimilarQuestionWorkflowState):
    """格式化输出节点"""
    return {
        "similar_questions": state["similar_questions"],
        "validation_results": state["validation_results"]
    }
```

---

## 📝 开发计划

| 任务 | 状态 | 负责人 |
|-----|------|--------|
| 创建目录结构 | ✅ 已完成 | - |
| 复制 Skill 文件 | ✅ 已完成 | - |
| 创建 state.py | ⬜ 待开始 | 后端 |
| 创建 graph.py | ⬜ 待开始 | 后端 |
| 创建 nodes.py | ⬜ 待开始 | 后端 |
| 实现 OCRService | ⬜ 待开始 | 后端 |
| 集成 Skill 调用 | ⬜ 待开始 | 后端 |
| 实现有效性校验 | ⬜ 待开始 | 后端 |
| 单元测试 | ⬜ 待开始 | 后端 |
| 集成测试 | ⬜ 待开始 | 后端 |

---

## 🧪 测试计划

### 单元测试

```python
# test_ocr_node.py
@pytest.mark.asyncio
async def test_ocr_recognize():
    state = {"image_url": "test_images/math_question.jpg"}
    result = await ocr_recognize_and_infer_params(state)
    assert result["ocr_result"]["question"] != ""
    assert result["ocr_result"]["confidence"] > 0.8
```

### 集成测试

```python
# test_workflow.py
@pytest.mark.asyncio
async def test_similar_question_workflow():
    workflow = create_similar_question_workflow()
    initial_state = {
        "image_url": "test_images/math_question.jpg",
        "retry_count": 0
    }
    result = await workflow.ainvoke(initial_state)
    assert len(result["similar_questions"]) == 3
    assert all(r["valid"] for r in result["validation_results"])
```

---

## 📚 相关文档

- **产品需求**：`docs/product/similar-question-prd.md`
- **开发计划**：`docs/planning/similar-question-dev-plan.md`
- **Skill 定义**：`backend/skills/similar-question-generation/SKILL.md`

---

**创建人**：后端团队  
**最后更新**：2026-05-12
