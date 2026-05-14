# 开发指南

> **版本**：1.0  
> **日期**：2026-04-28  
> **适用范围**：AI 出题助手项目

---

## 📋 目录

1. [快速开始](#快速开始)
2. [如何创建新 Skill](#如何创建新-skill)
3. [如何创建新 Workflow](#如何创建新-workflow)
4. [如何调试 Skill](#如何调试-skill)
5. [开发规范](#开发规范)
6. [常见问题](#常见问题)

---

## 快速开始

### 1. 环境准备

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key
```

#### 启动服务
```bash
python app/main.py
# 或
uvicorn app.main:app --reload
```

访问：http://localhost:8000

---

## 如何创建新 Skill

### Skill 的作用

Skill 是一个 **Markdown 策略文档**，用于指导 LLM 的行为，定义：
- 业务规则（如参数提取规则、场景策略）
- 追问逻辑
- 输出格式
- 质量标准

### 创建步骤

#### 步骤 1：创建 Skill 文件

```bash
touch backend/skills/my_new_skill.md
```

#### 步骤 2：定义 Skill 结构

```markdown
<skill name="my_new_skill" trigger="关键词1|关键词2|keyword">

# Skill 名称

## Purpose
简要说明这个 Skill 的目的

## When to Use
什么情况下使用这个 Skill

## Strategy

### Phase 1: 第一阶段名称
描述第一阶段的逻辑...

### Phase 2: 第二阶段名称
描述第二阶段的逻辑...

## Tools Available
- tool_name_1(param1, param2) - 工具描述
- tool_name_2(param1) - 工具描述

## Example Conversations
示例对话...

## Quality Checklist
- [ ] 质量检查项 1
- [ ] 质量检查项 2

</skill>
```

#### 步骤 3：测试 Skill

```python
from skills.loader import SkillLoader

loader = SkillLoader()

# 测试加载
user_input = "包含关键词的输入"
skill_content = loader.load_relevant_skills(user_input)
print(skill_content)
```

### Skill 编写规范

#### 1. **Trigger 关键词**
- 中英文都要包含
- 多个关键词用 `|` 分隔
- 示例：`"出题|生成试卷|create exam|generate exam"`

#### 2. **Strategy 分阶段**
- 每个阶段有明确的名称和目标
- 示例：`Phase 1: 参数收集`、`Phase 2: 场景匹配`

#### 3. **提供示例对话**
- 至少提供 2 个完整的对话示例
- 包含正常流程和异常情况

#### 4. **定义质量标准**
- Checklist 形式
- 可量化的标准

---

## 如何创建新 Workflow

### Workflow 的作用

Workflow 是一个 **LangGraph 流程图**，用于确定性执行多步流程，包含：
- 状态定义（State Schema）
- 节点函数（处理逻辑）
- 流程图（节点 + 边）

### 创建步骤

#### 步骤 1：创建目录结构

```bash
mkdir -p backend/workflows/my_new_workflow
cd backend/workflows/my_new_workflow
touch __init__.py state.py nodes.py graph.py
```

#### 步骤 2：定义状态（`state.py`）

```python
from typing import TypedDict, List, Dict, Optional

class MyWorkflowState(TypedDict):
    """Workflow 状态定义"""
    
    # 输入
    user_input: str
    session_id: str
    
    # 中间状态
    current_step: str
    intermediate_data: Dict
    
    # 输出
    final_result: Optional[Dict]
    error: Optional[str]


def create_initial_state(user_input: str, session_id: str) -> MyWorkflowState:
    """创建初始状态"""
    return MyWorkflowState(
        user_input=user_input,
        session_id=session_id,
        current_step="start",
        intermediate_data={},
        final_result=None,
        error=None
    )
```

#### 步骤 3：实现节点函数（`nodes.py`）

```python
from .state import MyWorkflowState

async def step1_process(state: MyWorkflowState) -> MyWorkflowState:
    """第一个处理步骤"""
    # 执行逻辑
    result = do_something(state["user_input"])
    
    # 更新状态
    state["intermediate_data"]["result1"] = result
    state["current_step"] = "step1_process"
    
    return state


async def step2_process(state: MyWorkflowState) -> MyWorkflowState:
    """第二个处理步骤"""
    # ...
    return state


def should_continue(state: MyWorkflowState) -> str:
    """决策函数：判断是否继续"""
    if state["intermediate_data"].get("result1"):
        return "continue"
    else:
        return "stop"
```

#### 步骤 4：定义流程图（`graph.py`）

```python
from langgraph.graph import StateGraph, END
from .state import MyWorkflowState
from . import nodes

def create_my_workflow() -> StateGraph:
    """创建 Workflow 流程图"""
    
    workflow = StateGraph(MyWorkflowState)
    
    # 添加节点
    workflow.add_node("step1", nodes.step1_process)
    workflow.add_node("step2", nodes.step2_process)
    
    # 设置入口
    workflow.set_entry_point("step1")
    
    # 添加边
    workflow.add_conditional_edges(
        "step1",
        nodes.should_continue,
        {
            "continue": "step2",
            "stop": END
        }
    )
    
    workflow.add_edge("step2", END)
    
    return workflow.compile()


def get_workflow():
    """获取编译后的 Workflow"""
    return create_my_workflow()
```

#### 步骤 5：导出（`__init__.py`）

```python
from .graph import get_workflow, create_my_workflow
from .state import MyWorkflowState, create_initial_state

__all__ = [
    "get_workflow",
    "create_my_workflow",
    "MyWorkflowState",
    "create_initial_state"
]
```

#### 步骤 6：注册到 MainAgent

```python
# backend/agents/main_agent.py

from workflows.my_new_workflow import get_workflow as get_my_workflow

class MainAgent:
    def __init__(self):
        self.workflows = {
            "exam": get_exam_workflow(),
            "my_new": get_my_workflow()  # 添加新 Workflow
        }
```

#### 步骤 7：测试 Workflow

```python
import asyncio
from workflows.my_new_workflow import get_workflow, create_initial_state

async def test():
    workflow = get_workflow()
    
    initial_state = create_initial_state(
        user_input="测试输入",
        session_id="test_001"
    )
    
    result = await workflow.ainvoke(initial_state)
    print(result)

asyncio.run(test())
```

---

## 如何调试 Skill

### 1. 单次测试（Playground）

```python
# backend/skill_debug/test_skill.py

from skills.loader import SkillLoader
from agents.main_agent import MainAgent

async def test_skill():
    agent = MainAgent()
    
    # 测试用例
    user_input = "帮我出份初二数学单元测验"
    
    result = await agent.execute(
        user_input=user_input,
        session_id="test_001"
    )
    
    print(f"需要追问: {result['needs_followup']}")
    print(f"追问消息: {result.get('followup_message')}")
    print(f"执行追踪: {result.get('execution_trace')}")

# 运行
asyncio.run(test_skill())
```

### 2. 批量测试

```python
# 创建测试用例文件
# backend/skill_debug/test_cases/exam_skill/cases.json

[
  {
    "id": "case_001",
    "input": "帮我出份初二数学试卷",
    "expected_output": {
      "needs_followup": true,
      "missing_params": ["knowledge_points"]
    }
  },
  {
    "id": "case_002",
    "input": "帮我出份初二数学单元测验，关于一元二次方程",
    "expected_output": {
      "needs_followup": false,
      "exam_id": "..."
    }
  }
]
```

```python
# 批量测试脚本
# backend/skill_debug/run_batch_test.py

import json
from agents.main_agent import MainAgent

async def run_batch_test(test_file: str):
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    agent = MainAgent()
    results = []
    
    for case in test_cases:
        result = await agent.execute(
            user_input=case["input"],
            session_id=f"test_{case['id']}"
        )
        
        # 对比预期输出
        passed = compare_result(result, case["expected_output"])
        
        results.append({
            "case_id": case["id"],
            "passed": passed,
            "result": result
        })
    
    # 统计通过率
    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    print(f"通过率: {pass_rate * 100}%")
    
    return results

asyncio.run(run_batch_test("skill_debug/test_cases/exam_skill/cases.json"))
```

### 3. A/B 测试

```python
# 对比两个 Skill 版本的效果

async def ab_test():
    # 使用版本 A
    skill_loader_a = SkillLoader()
    # 使用版本 B
    skill_loader_b = SkillLoader()
    
    test_cases = load_test_cases()
    
    results_a = run_tests_with_skill(skill_loader_a, test_cases)
    results_b = run_tests_with_skill(skill_loader_b, test_cases)
    
    # 对比指标
    print(f"版本 A 准确率: {results_a['accuracy']}")
    print(f"版本 B 准确率: {results_b['accuracy']}")
    
    if results_b['accuracy'] > results_a['accuracy']:
        print("推荐使用版本 B")
```

---

## 开发规范

### 1. 代码风格

#### Python
- 使用 `black` 格式化：`black .`
- 使用 `ruff` 检查：`ruff check .`
- 类型注解：所有函数必须有类型注解

#### 命名规范
- 文件名：小写下划线（`exam_workflow.py`）
- 类名：大驼峰（`ExamWorkflow`）
- 函数名：小写下划线（`extract_parameters`）
- 常量：全大写（`MAX_RETRY_COUNT`）

### 2. 注释规范

#### Docstring 格式
```python
async def extract_parameters(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    从对话中提取参数
    
    Args:
        state: 当前 Workflow 状态
    
    Returns:
        更新后的状态，包含 extracted_params
    
    Raises:
        ValueError: 参数格式错误时
    """
    pass
```

### 3. Git 提交规范

#### 提交消息格式
```
<type>(<scope>): <subject>

<body>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat(skill): 添加 adapt_skill 改编 Skill

- 支持提升/降低难度
- 支持改变题型
- 增加参考题目风格
```

### 4. 测试规范

#### 单元测试
```python
# tests/unit/test_skill_loader.py

import pytest
from skills.loader import SkillLoader

def test_load_relevant_skills():
    loader = SkillLoader()
    
    user_input = "帮我出份试卷"
    skills = loader.load_relevant_skills(user_input)
    
    assert "<skill" in skills
    assert "exam_skill" in skills

def test_load_skill_by_name():
    loader = SkillLoader()
    
    skill = loader.load_skill_by_name("exam_skill")
    assert skill is not None
```

#### 集成测试
```python
# tests/integration/test_exam_workflow.py

import pytest
from agents.main_agent import MainAgent

@pytest.mark.asyncio
async def test_exam_workflow_end_to_end():
    agent = MainAgent()
    
    result = await agent.execute(
        user_input="帮我出份初二数学单元测验，关于一元二次方程",
        session_id="test_001"
    )
    
    assert result["needs_followup"] == False
    assert result["result"]["exam_id"] is not None
```

---

## 常见问题

### Q1: Skill 没有被加载？

**原因**：Trigger 关键词不匹配

**解决**：
1. 检查 Skill 文件的 `trigger` 属性
2. 使用 `SkillLoader.get_skill_triggers("skill_name")` 查看触发词
3. 确保用户输入包含至少一个触发词

### Q2: Workflow 节点执行顺序不对？

**原因**：流程图定义错误

**解决**：
1. 使用 `visualize_workflow()` 函数生成 Mermaid 图
2. 检查 `add_edge` 和 `add_conditional_edges` 的顺序
3. 确保所有节点都有出口（要么到其他节点，要么到 END）

### Q3: LLM 调用失败？

**原因**：API Key 错误或网络问题

**解决**：
1. 检查 `.env` 文件中的 API Key
2. 测试 LLM 连接：`python scripts/test_llm_connection.py`
3. 切换到备用 LLM 提供商

### Q4: Elasticsearch 检索结果为空？

**原因**：索引未构建或查询错误

**解决**：
1. 运行 `python scripts/build_es_index.py` 构建索引
2. 检查 ES 服务是否启动：`curl http://localhost:9200`
3. 查看 ES 日志排查问题

### Q5: 如何查看 Workflow 执行追踪？

**方法**：
```python
result = await agent.execute(user_input="...", session_id="...")

# 查看执行追踪
for trace in result["execution_trace"]:
    print(f"步骤: {trace['step']}, 耗时: {trace['duration']}s")
```

---

## 联系方式

遇到问题？
- 📖 查看完整文档：`docs/`
- 💬 提交 Issue
- 📧 联系开发团队

---

**Happy Coding! 🚀**
