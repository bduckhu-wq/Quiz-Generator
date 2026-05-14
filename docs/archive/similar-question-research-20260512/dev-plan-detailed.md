# 相似题生成功能 - 后端开发计划

> **版本**：v1.0  
> **日期**：2026-05-12  
> **状态**：🟢 待开始  
> **阶段**：后端服务实现（优先）

---

## 📋 开发目标

**交付物**：
1. ✅ SimilarQuestionWorkflow（LangGraph 流程图）
2. ✅ SimilarQuestionAgent（Agent 实现）
3. ✅ similar-question-generation Skill（从蜜蜂家校迁移）
4. ✅ FastAPI 路由（3 个接口）
5. ✅ OCR 服务（DeepSeek-V4 Vision API）
6. ✅ API 文档（OpenAPI 规范）
7. ✅ 单元测试 + 集成测试

**验收标准**：
- 后端 API 可独立运行
- Postman 测试通过（上传图片 → 生成 3 道相似题）
- 单元测试覆盖率 ≥80%
- API 文档完整（Swagger UI 可访问）

---

## 🏗️ 技术架构

### 整体流程

```
POST /api/similar-question/upload
    ↓
OCR识别（DeepSeek-V4）
    ↓
POST /api/similar-question/generate
    ↓
SimilarQuestionAgent
    ↓
SimilarQuestionWorkflow
    ├─ ocr_recognize       # OCR识别节点（已完成）
    ├─ extract_params      # 参数提取节点
    ├─ generate_similar    # 生成相似题节点（调用Skill）
    └─ format_output       # 格式化输出节点
    ↓
返回 3 道相似题 JSON
```

### 目录结构

```
backend/
├── agents/
│   └── similar_question_agent.py       # 新增：相似题 Agent
│
├── workflows/
│   └── similar_question_workflow/      # 新增：相似题 Workflow
│       ├── __init__.py
│       ├── graph.py                    # LangGraph 流程图定义
│       ├── state.py                    # 状态定义
│       └── nodes.py                    # 节点实现
│
├── skills/
│   └── similar-question-generation/    # 新增：相似题生成 Skill
│       ├── SKILL.md                    # 从蜜蜂家校复制
│       ├── config.yaml                 # Skill 配置
│       └── prompt.txt                  # System Prompt
│
├── services/
│   └── ocr_service.py                  # 新增：OCR 服务
│
├── models/
│   └── similar_question.py             # 新增：相似题数据模型
│
├── app/
│   └── api/
│       └── similar_question.py         # 新增：FastAPI 路由
│
└── tests/
    └── test_similar_question/          # 新增：测试目录
        ├── test_ocr_service.py
        ├── test_workflow.py
        └── test_api.py
```

---

## 📝 开发任务清单

### Day 1：技术设计 + 环境准备

**任务 1.1：技术设计文档**
- [ ] 编写 `docs/architecture/similar-question-design.md`
  - 详细架构图
  - 数据流转
  - 错误处理
  - 性能优化
- [ ] 编写 `docs/reference/similar-question-api.md`
  - API 规范（OpenAPI 3.0）
  - 请求/响应示例
  - 错误码定义

**任务 1.2：DeepSeek-V4 Vision API 调研**
- [ ] 阅读 DeepSeek Vision API 文档
- [ ] 编写测试脚本（上传图片 → 识别文字）
- [ ] 验证准确率（至少 10 张测试图片）
- [ ] 记录 API 调用格式、参数、限流规则

**任务 1.3：环境配置**
- [ ] 配置 DeepSeek API Key（`.env` 文件）
- [ ] 安装依赖包（`langgraph`、`pydantic`、`deepseek-sdk`）
- [ ] 创建目录结构（按上面的目录树）

---

### Day 2-3：OCR 服务 + 数据模型

**任务 2.1：OCR 服务实现**

文件：`backend/services/ocr_service.py`

```python
"""
OCR 识别服务 - 使用 DeepSeek-V4 Vision API
"""

from typing import Dict
import httpx
from pydantic import BaseModel


class OCRResult(BaseModel):
    """OCR 识别结果"""
    question: str                # 题目内容
    options: list[str] = []      # 选项（可选）
    answer: str = ""             # 答案（可选）
    analysis: str = ""           # 解析（可选）
    
    # 推断参数
    subject: str                 # 学科
    grade: str                   # 年级
    knowledge_point: str         # 知识点
    question_type: str           # 题型
    difficulty: str              # 难度
    
    # 元数据
    confidence: float            # 识别置信度
    


class OCRService:
    """OCR 识别服务"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def recognize_question(self, image_url: str) -> OCRResult:
        """
        识别题目图片
        
        Args:
            image_url: 图片 URL（支持 HTTP/HTTPS 或 base64）
        
        Returns:
            OCRResult: 识别结果
        """
        prompt = self._build_prompt()
        
        response = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "temperature": 0.0,  # 识别任务不需要创造性
                "response_format": {"type": "json_object"}
            }
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 解析 JSON 响应
        content = result["choices"][0]["message"]["content"]
        data = json.loads(content)
        
        return OCRResult(**data)
    
    def _build_prompt(self) -> str:
        """构建 OCR 识别 Prompt"""
        return """
你是一个专业的题目识别助手。请识别图片中的题目内容，提取以下信息：

1. **题目内容**：完整的题目文字（保留原格式，包括换行）
2. **选项**（如有）：["A. xxx", "B. xxx", "C. xxx", "D. xxx"]
3. **答案**（如有）：如 "B" 或 "BC"（多选）
4. **解析**（如有）：详细解题步骤

5. **推断参数**：
   - subject: 学科（数学/语文/英语/物理/化学/生物/历史/地理/政治）
   - grade: 年级（小学三年级/初中一年级/高中二年级 等）
   - knowledge_point: 知识点（如"一元一次方程"、"勾股定理"）
   - question_type: 题型（选择题/填空题/解答题/判断题/应用题/证明题）
   - difficulty: 难度（简单/中等/困难）

6. **元数据**：
   - confidence: 识别置信度（0-1，如 0.95 表示 95% 确信）

**输出格式**：JSON（严格按照以下结构）

```json
{
  "question": "题目内容（包括题干）",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "answer": "B",
  "analysis": "解析内容",
  "subject": "数学",
  "grade": "初中二年级",
  "knowledge_point": "一元一次方程",
  "question_type": "选择题",
  "difficulty": "中等",
  "confidence": 0.95
}
```

**注意事项**：
- 如果是选择题，options 必须包含所有选项（A/B/C/D）
- 如果是主观题（解答题、应用题），options 为空数组 []
- 如果图片中没有答案或解析，对应字段为空字符串 ""
- knowledge_point 要精准到具体考点，不要太宽泛
- confidence 基于图片清晰度、文字识别难度综合判断

**数学公式处理**：
- 简单公式：直接用文字表示（如 "x^2 + 3x - 10 = 0"）
- 复杂公式：可使用 LaTeX 格式（如 "$\\frac{a}{b}$"）
"""
```

**任务 2.2：数据模型定义**

文件：`backend/models/similar_question.py`

```python
"""
相似题相关数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class QuestionType(str, Enum):
    """题型枚举"""
    CHOICE = "选择题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "解答题"
    TRUE_FALSE = "判断题"
    APPLICATION = "应用题"
    PROOF = "证明题"


class Difficulty(str, Enum):
    """难度枚举"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


class OriginalQuestion(BaseModel):
    """原题"""
    question: str = Field(..., description="题目内容")
    options: list[str] = Field(default_factory=list, description="选项（可选）")
    answer: str = Field(default="", description="答案（可选）")
    analysis: str = Field(default="", description="解析（可选）")
    image_url: Optional[str] = Field(None, description="原题截图 URL")
    
    # 元数据
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    knowledge_point: str = Field(..., description="知识点")
    question_type: QuestionType = Field(..., description="题型")
    difficulty: Difficulty = Field(..., description="难度")


class SimilarQuestion(BaseModel):
    """相似题"""
    id: str = Field(..., description="题目唯一 ID")
    question: str = Field(..., description="题目内容")
    options: list[str] = Field(default_factory=list, description="选项（可选）")
    answer: str = Field(..., description="答案")
    explanation: str = Field(..., description="详细解析")
    
    # 元数据
    subject: str = Field(..., description="学科")
    grade: str = Field(..., description="年级")
    knowledge_point: str = Field(..., description="知识点")
    question_type: QuestionType = Field(..., description="题型")
    difficulty: Difficulty = Field(..., description="难度")
    
    # 相似度信息
    similarity_level: float = Field(0.7, description="相似度（固定 70%）")
    changed_dimensions: list[str] = Field(
        default_factory=list, 
        description="变化维度（如 ['场景', '数值', '设问角度']）"
    )


class SimilarQuestionRequest(BaseModel):
    """生成相似题请求"""
    original_question: OriginalQuestion = Field(..., description="原题")
    count: int = Field(3, ge=1, le=5, description="生成数量（1-5，默认3）")
    similarity_level: float = Field(0.7, description="相似度（固定70%）")


class SimilarQuestionResponse(BaseModel):
    """生成相似题响应"""
    original_question: OriginalQuestion = Field(..., description="原题")
    similar_questions: list[SimilarQuestion] = Field(..., description="相似题列表")
    generation_time: float = Field(..., description="生成耗时（秒）")
    
    metadata: dict = Field(
        default_factory=dict,
        description="元数据（如 API 调用信息、Workflow 执行日志）"
    )
```

**任务 2.3：单元测试**

文件：`backend/tests/test_similar_question/test_ocr_service.py`

```python
"""
OCR 服务单元测试
"""

import pytest
from services.ocr_service import OCRService, OCRResult


@pytest.mark.asyncio
async def test_ocr_simple_text():
    """测试简单文字题识别"""
    service = OCRService(api_key="test_key")
    
    # 准备测试图片（简单文字题）
    image_url = "https://example.com/simple_question.jpg"
    
    result = await service.recognize_question(image_url)
    
    assert isinstance(result, OCRResult)
    assert result.question != ""
    assert result.subject in ["数学", "语文", "英语", "物理", "化学"]
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_ocr_math_formula():
    """测试数学公式题识别"""
    service = OCRService(api_key="test_key")
    
    # 准备测试图片（含数学公式）
    image_url = "https://example.com/math_formula.jpg"
    
    result = await service.recognize_question(image_url)
    
    assert "^" in result.question or "$" in result.question  # 包含公式符号
    assert result.subject == "数学"


@pytest.mark.asyncio
async def test_ocr_choice_question():
    """测试选择题识别"""
    service = OCRService(api_key="test_key")
    
    # 准备测试图片（选择题）
    image_url = "https://example.com/choice_question.jpg"
    
    result = await service.recognize_question(image_url)
    
    assert result.question_type == "选择题"
    assert len(result.options) == 4  # A/B/C/D 四个选项
    assert result.answer in ["A", "B", "C", "D"]
```

---

### Day 4-6：Workflow + Skill 集成

**任务 3.1：Skill 迁移**

从蜜蜂家校项目复制文件：
```bash
# 1. 复制 SKILL.md
cp "/Users/pinya_hu/Desktop/tare SOLO beta/蜜蜂家校/similar-question-generation/SKILL.md" \
   backend/skills/similar-question-generation/

# 2. 创建 config.yaml
# 3. 创建 prompt.txt（从 SKILL.md 提取）
```

文件：`backend/skills/similar-question-generation/config.yaml`

```yaml
name: similar-question-generation
description: 基于原题生成保持核心学习目标但表层维度变化的相似题
version: 4.0
author: 教研团队

parameters:
  similarity_level: 0.7  # 固定 70% 相似度
  count: 3               # 固定生成 3 道
  
  change_rules:
    core_layer: 0%             # 核心层锁定（知识点、数学模型、解题逻辑）
    structure_layer: 10%       # 结构层最多 10%（至少改1处）
    expression_layer: 30-50%   # 表达层 30-50%（场景陌生化）
    value_layer: 80-100%       # 数值层 80-100%（大幅改变）

output_format: json
model: deepseek-chat
temperature: 0.7
max_tokens: 4000
```

文件：`backend/skills/similar-question-generation/prompt.txt`

```
你是蜜蜂家校的相似题生成专家，精通四层可控模型（核心层/结构层/表达层/数值层）。

## 任务
基于用户提供的原题，生成 3 道相似题，要求：
- **核心层（0% 变化，锁死）**：知识点、数学模型、解题逻辑、能力考查层级完全不变
- **结构层（≤10% 变化）**：至少改变 1 处（设问角度/求解对象/干扰项类型）
- **表达层（30-50% 变化）**：场景完全陌生化（如环形跑道→公交环线→工程建设）
- **数值层（80-100% 变化）**：具体数字、数量级大幅改变

## 四层控制模型详解

[从 SKILL.md 完整复制规则，此处省略...]

## 干扰项设计原则

**所有干扰项必须来自对核心模型的真实误解，禁止硬塞无关约束。**

[从 SKILL.md 完整复制规则，此处省略...]

## 输出格式

生成 3 道相似题，输出 JSON 数组：

```json
[
  {
    "question": "题目内容（含题干和选项）",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "B",
    "explanation": "详细解析，包括：1) 核心数学模型 2) 解题步骤 3) 干扰项分析"
  },
  {
    "question": "...",
    "options": [...],
    "answer": "...",
    "explanation": "..."
  },
  {
    "question": "...",
    "options": [...],
    "answer": "...",
    "explanation": "..."
  }
]
```

## 质量检查清单

生成后自检：
- [ ] 核心层未改变（知识点、模型、逻辑相同）
- [ ] 场景已陌生化（完全不同的情境）
- [ ] 数值已大幅改变（80%+ 不同）
- [ ] 结构层至少改 1 处（设问角度/求解对象/干扰项等）
- [ ] 干扰项来自真实误解（不是硬塞的无关条件）
- [ ] 题目可作答（条件充分、计算合理、答案唯一）
```

**任务 3.2：Workflow 实现**

文件：`backend/workflows/similar_question_workflow/state.py`

```python
"""
SimilarQuestionWorkflow 状态定义
"""

from typing import TypedDict, Optional
from models.similar_question import OriginalQuestion, SimilarQuestion


class SimilarQuestionWorkflowState(TypedDict):
    """相似题生成 Workflow 状态"""
    
    # 输入
    image_url: Optional[str]                # 原题截图 URL
    original_question: Optional[OriginalQuestion]  # 原题（OCR 识别后）
    
    # 中间状态
    ocr_result: Optional[dict]              # OCR 识别原始结果
    extracted_params: Optional[dict]        # 提取的参数
    skill_input: Optional[dict]             # Skill 输入
    skill_output: Optional[list]            # Skill 输出（3 道相似题）
    
    # 输出
    similar_questions: list[SimilarQuestion]  # 最终相似题列表
    
    # 元数据
    error: Optional[str]                    # 错误信息
    workflow_log: list[str]                 # 工作流日志
```

文件：`backend/workflows/similar_question_workflow/nodes.py`

```python
"""
SimilarQuestionWorkflow 节点实现
"""

from .state import SimilarQuestionWorkflowState
from services.ocr_service import OCRService
from models.similar_question import OriginalQuestion, SimilarQuestion
import os
import uuid


def ocr_recognize(state: SimilarQuestionWorkflowState) -> SimilarQuestionWorkflowState:
    """
    节点 1：OCR 识别原题
    """
    image_url = state["image_url"]
    
    if not image_url:
        state["error"] = "缺少图片 URL"
        return state
    
    # 调用 OCR 服务
    ocr_service = OCRService(api_key=os.getenv("DEEPSEEK_API_KEY"))
    ocr_result = await ocr_service.recognize_question(image_url)
    
    # 保存 OCR 结果
    state["ocr_result"] = ocr_result.dict()
    state["workflow_log"].append("OCR 识别完成")
    
    return state


def extract_params(state: SimilarQuestionWorkflowState) -> SimilarQuestionWorkflowState:
    """
    节点 2：参数提取
    """
    ocr_result = state["ocr_result"]
    
    # 将 OCR 结果转换为 OriginalQuestion
    original_question = OriginalQuestion(
        question=ocr_result["question"],
        options=ocr_result["options"],
        answer=ocr_result["answer"],
        analysis=ocr_result["analysis"],
        image_url=state["image_url"],
        subject=ocr_result["subject"],
        grade=ocr_result["grade"],
        knowledge_point=ocr_result["knowledge_point"],
        question_type=ocr_result["question_type"],
        difficulty=ocr_result["difficulty"]
    )
    
    state["original_question"] = original_question
    state["extracted_params"] = original_question.dict()
    state["workflow_log"].append("参数提取完成")
    
    return state


def generate_similar(state: SimilarQuestionWorkflowState) -> SimilarQuestionWorkflowState:
    """
    节点 3：生成相似题（调用 Skill）
    """
    original_question = state["original_question"]
    
    # 构建 Skill 输入
    skill_input = {
        "original_question": original_question.dict(),
        "count": 3,
        "similarity_level": 0.7
    }
    
    # 调用 similar-question-generation Skill
    # TODO: 实际调用 LLM + Skill Prompt
    # 此处简化为伪代码
    llm_response = await call_skill_llm(skill_input)
    
    state["skill_output"] = llm_response  # List of 3 questions
    state["workflow_log"].append("相似题生成完成")
    
    return state


def format_output(state: SimilarQuestionWorkflowState) -> SimilarQuestionWorkflowState:
    """
    节点 4：格式化输出
    """
    skill_output = state["skill_output"]
    original_question = state["original_question"]
    
    # 将 Skill 输出转换为 SimilarQuestion 列表
    similar_questions = []
    for i, item in enumerate(skill_output):
        similar_question = SimilarQuestion(
            id=str(uuid.uuid4()),
            question=item["question"],
            options=item.get("options", []),
            answer=item["answer"],
            explanation=item["explanation"],
            subject=original_question.subject,
            grade=original_question.grade,
            knowledge_point=original_question.knowledge_point,
            question_type=original_question.question_type,
            difficulty=original_question.difficulty,
            similarity_level=0.7,
            changed_dimensions=["场景", "数值", "表述"]  # 固定维度
        )
        similar_questions.append(similar_question)
    
    state["similar_questions"] = similar_questions
    state["workflow_log"].append("输出格式化完成")
    
    return state
```

文件：`backend/workflows/similar_question_workflow/graph.py`

```python
"""
SimilarQuestionWorkflow 流程图定义
"""

from langgraph.graph import StateGraph, END
from .state import SimilarQuestionWorkflowState
from . import nodes


def create_similar_question_workflow() -> StateGraph:
    """
    创建相似题生成 Workflow
    
    流程：
    1. OCR 识别 → 提取参数
    2. 生成相似题（调用 Skill）
    3. 格式化输出
    4. END
    """
    
    workflow = StateGraph(SimilarQuestionWorkflowState)
    
    # 添加节点
    workflow.add_node("ocr_recognize", nodes.ocr_recognize)
    workflow.add_node("extract_params", nodes.extract_params)
    workflow.add_node("generate_similar", nodes.generate_similar)
    workflow.add_node("format_output", nodes.format_output)
    
    # 设置入口
    workflow.set_entry_point("ocr_recognize")
    
    # 定义边
    workflow.add_edge("ocr_recognize", "extract_params")
    workflow.add_edge("extract_params", "generate_similar")
    workflow.add_edge("generate_similar", "format_output")
    workflow.add_edge("format_output", END)
    
    return workflow.compile()
```

**任务 3.3：Agent 实现**

文件：`backend/agents/similar_question_agent.py`

```python
"""
SimilarQuestionAgent - 相似题生成 Agent
"""

from workflows.similar_question_workflow.graph import create_similar_question_workflow
from workflows.similar_question_workflow.state import SimilarQuestionWorkflowState
from models.similar_question import SimilarQuestionResponse, OriginalQuestion
import time


class SimilarQuestionAgent:
    """相似题生成 Agent"""
    
    def __init__(self):
        self.workflow = create_similar_question_workflow()
    
    async def generate(
        self, 
        image_url: str = None,
        original_question: OriginalQuestion = None
    ) -> SimilarQuestionResponse:
        """
        生成相似题
        
        Args:
            image_url: 原题截图 URL（OCR 识别）
            original_question: 原题对象（已知题目内容，跳过 OCR）
        
        Returns:
            SimilarQuestionResponse: 相似题响应
        """
        start_time = time.time()
        
        # 初始化状态
        initial_state: SimilarQuestionWorkflowState = {
            "image_url": image_url,
            "original_question": original_question,
            "ocr_result": None,
            "extracted_params": None,
            "skill_input": None,
            "skill_output": None,
            "similar_questions": [],
            "error": None,
            "workflow_log": []
        }
        
        # 执行 Workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # 检查错误
        if final_state.get("error"):
            raise ValueError(final_state["error"])
        
        # 构建响应
        generation_time = time.time() - start_time
        
        response = SimilarQuestionResponse(
            original_question=final_state["original_question"],
            similar_questions=final_state["similar_questions"],
            generation_time=generation_time,
            metadata={
                "workflow_log": final_state["workflow_log"],
                "ocr_confidence": final_state["ocr_result"].get("confidence") if final_state.get("ocr_result") else None
            }
        )
        
        return response
```

---

### Day 7-8：FastAPI 路由 + 测试

**任务 4.1：FastAPI 路由实现**

文件：`backend/app/api/similar_question.py`

```python
"""
相似题 API 路由
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from models.similar_question import (
    SimilarQuestionRequest,
    SimilarQuestionResponse,
    OriginalQuestion
)
from agents.similar_question_agent import SimilarQuestionAgent
import uuid
import os
import json


router = APIRouter(prefix="/api/similar-question", tags=["相似题生成"])


@router.post("/upload", summary="上传原题截图")
async def upload_original_question(image: UploadFile = File(...)):
    """
    上传原题截图，OCR 识别
    
    **流程**：
    1. 保存图片到临时目录
    2. 调用 OCR 服务识别
    3. 返回识别结果（OriginalQuestion）
    """
    # 保存图片
    image_id = str(uuid.uuid4())
    image_path = f"/tmp/similar_question_{image_id}.jpg"
    
    with open(image_path, "wb") as f:
        content = await image.read()
        f.write(content)
    
    # OCR 识别
    agent = SimilarQuestionAgent()
    
    try:
        # 仅执行 OCR 节点
        response = await agent.generate(image_url=f"file://{image_path}")
        original_question = response.original_question
        
        return {
            "success": True,
            "data": original_question.dict(),
            "message": "识别成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败：{str(e)}")


@router.post("/generate", summary="生成相似题", response_model=SimilarQuestionResponse)
async def generate_similar_questions(request: SimilarQuestionRequest):
    """
    生成 3 道相似题
    
    **流程**：
    1. 接收原题参数
    2. 调用 SimilarQuestionAgent
    3. 返回 3 道相似题
    """
    agent = SimilarQuestionAgent()
    
    try:
        response = await agent.generate(
            original_question=request.original_question
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")


@router.post("/generate/stream", summary="流式生成相似题")
async def generate_similar_questions_stream(request: SimilarQuestionRequest):
    """
    流式生成相似题（SSE）
    
    **流程**：
    1. 每生成 1 道题实时推送
    2. 前端可实时展示进度
    """
    async def event_generator():
        agent = SimilarQuestionAgent()
        
        yield f"data: {json.dumps({'stage': 'start', 'total': 3})}\n\n"
        
        # TODO: 实现流式生成（需要 Workflow 支持）
        # 此处简化为逐个返回
        
        response = await agent.generate(original_question=request.original_question)
        
        for i, question in enumerate(response.similar_questions, 1):
            yield f"data: {json.dumps({'stage': 'generating', 'index': i, 'question': question.dict()})}\n\n"
        
        yield f"data: {json.dumps({'stage': 'done'})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{question_id}/regenerate", summary="重新生成单道题")
async def regenerate_single_question(
    question_id: str,
    request: SimilarQuestionRequest
):
    """
    重新生成单道相似题
    
    **流程**：
    1. 接收原题 + 题目 ID
    2. 重新生成 1 道相似题
    3. 返回新题
    """
    agent = SimilarQuestionAgent()
    
    try:
        # 生成 1 道题
        response = await agent.generate(original_question=request.original_question)
        new_question = response.similar_questions[0]  # 取第一道
        
        return {
            "success": True,
            "data": new_question.dict(),
            "message": "重新生成成功"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败：{str(e)}")
```

**任务 4.2：集成测试**

文件：`backend/tests/test_similar_question/test_api.py`

```python
"""
API 集成测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_upload_and_generate():
    """
    测试完整流程：上传截图 → 生成相似题
    """
    # 1. 上传图片
    with open("tests/fixtures/sample_question.jpg", "rb") as f:
        response = client.post(
            "/api/similar-question/upload",
            files={"image": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    original_question = data["data"]
    
    # 2. 生成相似题
    response = client.post(
        "/api/similar-question/generate",
        json={
            "original_question": original_question,
            "count": 3,
            "similarity_level": 0.7
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    
    assert len(result["similar_questions"]) == 3
    assert result["generation_time"] > 0
    
    # 验证相似题质量
    for question in result["similar_questions"]:
        assert question["question"] != original_question["question"]  # 不是原题
        assert question["knowledge_point"] == original_question["knowledge_point"]  # 知识点相同
```

---

### Day 9：API 文档 + 部署

**任务 5.1：API 文档**

文件：`docs/reference/similar-question-api.md`

```markdown
# 相似题生成 API 规范

## 1. 上传原题截图

**接口**：`POST /api/similar-question/upload`

**请求**：
- Content-Type: multipart/form-data
- Body: image (文件流)

**响应**：
```json
{
  "success": true,
  "data": {
    "question": "题目内容",
    "options": ["A. xxx", "B. xxx", "C. xxx", "D. xxx"],
    "answer": "B",
    "subject": "数学",
    "grade": "初二",
    "knowledge_point": "一元一次方程",
    "question_type": "选择题",
    "difficulty": "中等"
  },
  "message": "识别成功"
}
```

## 2. 生成相似题

**接口**：`POST /api/similar-question/generate`

**请求**：
```json
{
  "original_question": {
    "question": "...",
    "options": [...],
    "answer": "...",
    "subject": "数学",
    "grade": "初二",
    "knowledge_point": "一元一次方程",
    "question_type": "选择题",
    "difficulty": "中等"
  },
  "count": 3,
  "similarity_level": 0.7
}
```

**响应**：
```json
{
  "original_question": {...},
  "similar_questions": [
    {
      "id": "uuid",
      "question": "...",
      "options": [...],
      "answer": "...",
      "explanation": "..."
    },
    {...},
    {...}
  ],
  "generation_time": 15.2,
  "metadata": {
    "workflow_log": [...],
    "ocr_confidence": 0.95
  }
}
```

## 3. 流式生成（SSE）

**接口**：`POST /api/similar-question/generate/stream`

**事件流**：
```
data: {"stage": "start", "total": 3}

data: {"stage": "generating", "index": 1, "question": {...}}

data: {"stage": "generating", "index": 2, "question": {...}}

data: {"stage": "generating", "index": 3, "question": {...}}

data: {"stage": "done"}
```
```

**任务 5.2：部署脚本**

```bash
# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**任务 5.3：Postman 测试集**

创建 Postman Collection：
- 上传图片测试
- 生成相似题测试
- 流式生成测试
- 重新生成单题测试

---

## ✅ 验收标准

### 功能验收
- [ ] 上传图片后能正确识别题目内容（准确率 ≥90%）
- [ ] 生成的 3 道相似题保持核心知识点不变
- [ ] 相似题场景已陌生化（不是简单数字替换）
- [ ] 相似题答案正确、逻辑严密
- [ ] API 响应时间 ≤20 秒（P95）

### 技术验收
- [ ] 单元测试覆盖率 ≥80%
- [ ] 集成测试通过（Postman 全部用例）
- [ ] API 文档完整（Swagger UI 可访问）
- [ ] 错误处理完善（图片识别失败、生成失败等）
- [ ] 日志记录完整（Workflow 执行日志）

### 文档验收
- [ ] `docs/architecture/similar-question-design.md` 完整
- [ ] `docs/reference/similar-question-api.md` 完整
- [ ] 代码注释清晰（关键函数有 docstring）
- [ ] README 更新（新增相似题功能说明）

---

## 📅 时间线

| 日期 | 任务 | 状态 |
|-----|------|------|
| Day 1 | 技术设计 + 环境准备 | ⬜ 待开始 |
| Day 2-3 | OCR 服务 + 数据模型 | ⬜ 待开始 |
| Day 4-6 | Workflow + Skill 集成 | ⬜ 待开始 |
| Day 7-8 | FastAPI 路由 + 测试 | ⬜ 待开始 |
| Day 9 | API 文档 + 部署 | ⬜ 待开始 |

**预计完成**：2026-05-21（2 周后）

---

## 🚀 启动命令

**确认后端开发计划后，执行以下命令启动开发**：

```bash
# 1. 创建分支
git checkout -b feature/similar-question-backend

# 2. 创建目录结构
mkdir -p backend/{agents,workflows/similar_question_workflow,skills/similar-question-generation,services,tests/test_similar_question}

# 3. 复制 Skill 文件
cp "/Users/pinya_hu/Desktop/tare SOLO beta/蜜蜂家校/similar-question-generation/SKILL.md" backend/skills/similar-question-generation/

# 4. 安装依赖
pip install deepseek-sdk langgraph pydantic httpx

# 5. 配置环境变量
echo "DEEPSEEK_API_KEY=your_key_here" >> .env

# 6. 开始编码！
```

---

**文档维护者**：后端团队  
**最后更新**：2026-05-12  
**状态**：🟢 待开始
