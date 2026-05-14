---
name: code-style
description: 代码风格与质量规范
---

# 代码风格规范

## 通用原则

### 1. 命名规范
- **文件名**：小写下划线（如 `exam_agent.py`、`question_types.ts`）
- **类名**：大驼峰（如 `ExamAgent`、`QuestionGenerator`）
- **函数/方法**：小写下划线（Python）或小驼峰（JavaScript/TypeScript）
- **常量**：全大写下划线（如 `MAX_RETRY_COUNT`、`DEFAULT_SCENE`）

### 2. 注释规范
- **关键业务逻辑必须注释**：参数提取、场景策略匹配、Agent 决策点
- **中文注释优先**：面向产品经理和未来维护者
- **避免冗余注释**：如 `i += 1 # 递增` 无意义

### 3. 函数/方法长度
- 单个函数不超过 **50 行**（不含注释和空行）
- 超过 30 行时考虑拆分子函数
- 嵌套层级不超过 **3 层**

---

## Python 后端规范

### 1. 类型注解
**必须使用类型注解**，提升代码可读性和 IDE 支持。

```python
# ✅ 推荐
def generate_exam(
    subject: str,
    grade: str,
    scene: ExamScene,
    difficulty_dist: dict[Difficulty, float]
) -> ExamResponse:
    ...

# ❌ 不推荐
def generate_exam(subject, grade, scene, difficulty_dist):
    ...
```

### 2. 枚举类型
使用 `enum.Enum` 定义枚举，避免字符串硬编码。

```python
from enum import Enum

class ExamScene(str, Enum):
    HOMEWORK = "homework"
    UNIT_TEST = "unit_test"
    EXAM = "exam"
    REVIEW = "review"
```

### 3. 数据模型
使用 Pydantic 定义数据模型，自动校验和序列化。

```python
from pydantic import BaseModel, Field

class Question(BaseModel):
    id: str = Field(..., description="题目唯一ID")
    type: QuestionType
    difficulty: Difficulty
    score: int = Field(gt=0, description="分值必须大于0")
    content: str
    answer: str
```

### 4. 错误处理
- **明确异常类型**：避免裸 `except`
- **日志记录**：关键异常必须记录到日志

```python
# ✅ 推荐
try:
    result = llm_client.generate(prompt)
except TimeoutError as e:
    logger.error(f"LLM 调用超时：{e}")
    raise HTTPException(status_code=504, detail="生成超时，请重试")

# ❌ 不推荐
try:
    result = llm_client.generate(prompt)
except:
    pass
```

### 5. Agent 相关
- **System Prompt 外部化**：存放在 `skills/` 目录，不硬编码在代码中
- **工具定义清晰**：每个工具必须有 docstring 和参数说明

```python
def generate_exam(
    subject: str,
    grade: str,
    scene: ExamScene,
    difficulty_dist: dict[Difficulty, float],
    question_count: int
) -> list[Question]:
    """
    生成试卷题目数组。

    Args:
        subject: 学科（如"数学"、"物理"）
        grade: 年级（如"初二"、"高一"）
        scene: 出题场景（课后作业/单元测验/期中期末/考前复习）
        difficulty_dist: 难度分布（如 {"easy": 0.2, "medium": 0.5, "hard": 0.3}）
        question_count: 总题数

    Returns:
        题目数组，按题型分组排列
    """
    ...
```

---

## JavaScript/TypeScript 前端规范

### 1. 组件结构
- **函数组件优先**：使用 React Hooks
- **单一职责**：每个组件只负责一个功能模块

```tsx
// ✅ 推荐
const ParameterPanel: React.FC<ParameterPanelProps> = ({ params, onConfirm }) => {
  return (
    <div className="parameter-panel">
      <DifficultySlider value={params.difficulty} />
      <QuestionTypeSelector types={params.questionTypes} />
      <button onClick={onConfirm}>确认并生成</button>
    </div>
  );
};

// ❌ 不推荐（组件过大，混合多个职责）
const ExamPage = () => {
  // 200+ 行代码，包含对话、参数面板、试卷预览...
};
```

### 2. 类型定义
使用 TypeScript 接口定义数据结构，与后端 JSON 格式对齐。

```typescript
// 与 PRD 8.2 节对齐
interface Question {
  id: string;
  index: number;
  type: QuestionType;
  difficulty: Difficulty;
  score: number;
  content: string;
  options?: Option[];
  answer: string;
  analysis?: string;
  knowledgePoints: string[];
}
```

### 3. SSE 流式处理
```typescript
// ✅ 推荐
const streamResponse = async (sessionId: string) => {
  const response = await fetch(`/api/chat/${sessionId}/stream`);
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const events = parseSSEEvents(chunk);
    events.forEach(event => handleSSEEvent(event));
  }
};
```

---

## 禁忌事项

### ❌ 严禁
- **硬编码敏感信息**：API Key、数据库密码等必须使用环境变量
- **直接修改 PRD.md**：除非经过明确讨论并记录变更原因
- **跳过类型注解**：Python 和 TypeScript 必须使用类型系统
- **忽略边界条件**：如空输入、异常参数、网络超时

### ⚠️ 避免
- **过早优化**：先保证功能正确，再考虑性能
- **过度抽象**：三次重复再抽象，避免过早设计模式
- **魔法数字**：如 `if count > 10` 应改为 `if count > MAX_QUESTION_COUNT`

---

## 代码审查 Checklist

提交代码前，自检以下项目：

- [ ] 所有函数/方法包含类型注解（Python）或类型定义（TypeScript）
- [ ] 关键业务逻辑有注释说明
- [ ] 错误处理完整（不使用裸 `except` 或 `catch`）
- [ ] 日志记录关键操作（Agent 调用、工具执行、异常）
- [ ] 边界条件已测试（空输入、异常参数）
- [ ] 符合 PRD 定义（参数规则、场景策略、API 格式）
- [ ] 无硬编码敏感信息（API Key、密码）
- [ ] 文件命名符合规范（小写下划线）

---

## 版本记录

- v1.0 (2026-04-27): 初始版本，建立基础代码规范
