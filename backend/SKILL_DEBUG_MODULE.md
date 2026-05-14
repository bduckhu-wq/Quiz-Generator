# Skill 迭代调试模块设计

## 目录结构扩展

```
AI_quiz_new/
├── backend/
│   ├── skills/                           # 🆕 Skill 配置与管理
│   │   ├── __init__.py
│   │   ├── definitions/                  # Skill 定义文件（YAML/JSON）
│   │   │   ├── exam_skill_v1.0.yaml      # 出题 Skill v1.0
│   │   │   ├── exam_skill_v1.1.yaml      # 出题 Skill v1.1（迭代版本）
│   │   │   ├── adapt_skill_v1.0.yaml     # 改编 Skill v1.0
│   │   │   └── _archive/                 # 历史版本归档
│   │   │       └── exam_skill_v0.9.yaml
│   │   ├── loader.py                     # Skill 加载器
│   │   │   # class SkillLoader:
│   │   │   #     def load(skill_name, version) -> SkillConfig
│   │   │   #     def list_versions(skill_name) -> list
│   │   │   #     def validate(skill_config) -> bool
│   │   ├── executor.py                   # Skill 执行器
│   │   │   # class SkillExecutor:
│   │   │   #     def execute(skill_config, input_data) -> result
│   │   │   #     def execute_with_trace(skill_config, input_data) -> (result, trace)
│   │   ├── validator.py                  # Skill 验证器
│   │   │   # class SkillValidator:
│   │   │   #     def validate_config(config) -> list[Error]
│   │   │   #     def validate_output(output, expected_schema) -> bool
│   │   └── registry.py                   # Skill 注册中心
│   │       # 管理所有可用的 Skill 及其版本
│   │
│   ├── skill_debug/                      # 🆕 Skill 调试平台
│   │   ├── __init__.py
│   │   ├── api/                          # 调试 API 接口
│   │   │   ├── __init__.py
│   │   │   ├── playground.py             # Skill 测试场（单次执行）
│   │   │   ├── batch_test.py             # 批量测试
│   │   │   ├── ab_test.py                # A/B 测试
│   │   │   ├── metrics.py                # 效果指标查询
│   │   │   └── versions.py               # 版本管理
│   │   ├── evaluators/                   # 🆕 效果评估器
│   │   │   ├── __init__.py
│   │   │   ├── parameter_evaluator.py    # 参数提取准确性评估
│   │   │   │   # class ParameterEvaluator:
│   │   │   │   #     def evaluate(extracted, expected) -> dict
│   │   │   │   #     计算：准确率、召回率、F1
│   │   │   ├── question_evaluator.py     # 题目质量评估
│   │   │   │   # class QuestionEvaluator:
│   │   │   │   #     def evaluate(questions, criteria) -> dict
│   │   │   │   #     评估：知识点匹配度、难度准确性、题目质量
│   │   │   ├── scene_evaluator.py        # 场景策略评估
│   │   │   │   # 评估难度分布、题型分布是否符合策略
│   │   │   └── user_evaluator.py         # 用户满意度评估
│   │   │       # 统计：教师评分、题目采用率、修改率
│   │   ├── test_cases/                   # 🆕 测试用例库
│   │   │   ├── __init__.py
│   │   │   ├── parameter_extraction/     # 参数提取测试用例
│   │   │   │   ├── cases.json            # 标准测试用例
│   │   │   │   │   # [
│   │   │   │   │   #   {
│   │   │   │   │   #     "id": "case_001",
│   │   │   │   │   #     "input": "帮我出份初二数学单元测验，关于一元二次方程",
│   │   │   │   │   #     "expected": {
│   │   │   │   │   #       "subject": "数学",
│   │   │   │   │   #       "grade": "初二",
│   │   │   │   │   #       "knowledge_points": ["一元二次方程"],
│   │   │   │   │   #       "scene": "unit_test"
│   │   │   │   │   #     }
│   │   │   │   │   #   }
│   │   │   │   │   # ]
│   │   │   │   └── edge_cases.json       # 边界测试用例
│   │   │   ├── scene_matching/           # 场景匹配测试用例
│   │   │   │   └── cases.json
│   │   │   └── question_generation/      # 题目生成测试用例
│   │   │       └── cases.json
│   │   ├── reports/                      # 🆕 测试报告存储
│   │   │   ├── {timestamp}_skill_v1.0_vs_v1.1.json
│   │   │   └── {timestamp}_batch_test_result.json
│   │   └── traces/                       # 🆕 执行追踪记录
│   │       └── {session_id}_trace.json   # 每次执行的详细追踪
│   │
│   ├── app/api/v1/
│   │   └── skill_debug.py                # 🆕 Skill 调试接口（挂载到 FastAPI）
│   │
│   └── services/
│       └── skill_service.py              # 🆕 Skill 业务逻辑封装
│
├── skill-debug-ui/                       # 🆕 Skill 调试 Web 界面（独立前端项目）
│   ├── src/
│   │   ├── pages/
│   │   │   ├── playground.tsx            # Skill 测试场页面
│   │   │   ├── batch-test.tsx            # 批量测试页面
│   │   │   ├── ab-test.tsx               # A/B 测试页面
│   │   │   ├── metrics.tsx               # 效果指标页面
│   │   │   └── version-manage.tsx        # 版本管理页面
│   │   ├── components/
│   │   │   ├── SkillConfigEditor.tsx     # Skill 配置编辑器（Monaco Editor）
│   │   │   ├── TraceViewer.tsx           # 执行追踪可视化
│   │   │   ├── MetricsChart.tsx          # 指标图表
│   │   │   └── DiffViewer.tsx            # Skill 版本对比
│   │   └── lib/
│   │       └── api.ts                    # 调试 API 客户端
│   └── package.json
│
└── docs/
    └── skill_debug_guide.md              # 🆕 Skill 调试指南
```

---

## 核心模块详解

### 1. Skill 定义文件（YAML 格式）

**`backend/skills/definitions/exam_skill_v1.0.yaml`**

```yaml
# Skill 元信息
metadata:
  name: "exam_skill"
  version: "1.0"
  description: "出题 Skill - 基础版本"
  author: "教研团队"
  created_at: "2026-04-28"
  tags: ["出题", "参数提取", "场景策略"]

# Prompt 模板
prompts:
  system_prompt: |
    你是一个专业的 K12 出题助手。通过多轮对话理解教师需求并生成试卷。
    
    # 参数提取规则
    必须提取：学科、年级、知识点
    可选提取：场景（作业/测验/考试/复习）
    
    # 追问策略
    - 缺失学科/年级 → 直接询问
    - 缺失知识点 → 提供常见选项 + 自由输入
    - 缺失场景 → 根据关键词推断或询问
  
  parameter_extraction_prompt: |
    从以下对话中提取结构化参数：
    {conversation_history}
    
    请以 JSON 格式返回：
    {{
      "subject": "学科",
      "grade": "年级",
      "knowledge_points": ["知识点1", "知识点2"],
      "scene": "场景（可选）"
    }}
  
  followup_prompt: |
    当前已提取参数：{extracted_params}
    缺失参数：{missing_params}
    
    请生成一个友好的追问，引导教师补充缺失信息。

# 参数提取规则
parameter_extraction:
  required_fields:
    - name: "subject"
      type: "string"
      description: "学科"
      examples: ["数学", "物理", "化学", "语文"]
      validation:
        enum: ["数学", "物理", "化学", "生物", "语文", "英语", "历史", "地理", "政治"]
    
    - name: "grade"
      type: "string"
      description: "年级"
      examples: ["初一", "初二", "高三"]
      validation:
        enum: ["初一", "初二", "初三", "高一", "高二", "高三"]
    
    - name: "knowledge_points"
      type: "array"
      description: "知识点列表"
      examples: [["一元二次方程"], ["函数", "二次函数"]]
      validation:
        min_items: 1
        max_items: 5
  
  optional_fields:
    - name: "scene"
      type: "string"
      description: "出题场景"
      default: "unit_test"  # 默认值
      examples: ["homework", "unit_test", "exam", "review"]

# 场景策略配置
scene_strategies:
  homework:
    description: "课后作业：侧重基础巩固"
    difficulty_distribution:
      easy: 0.5
      medium: 0.4
      hard: 0.1
    question_type_distribution:
      choice: 0.3
      blank: 0.4
      solution: 0.3
    total_count_range: [8, 15]
    total_score: 100
  
  unit_test:
    description: "单元测验：全面考查"
    difficulty_distribution:
      easy: 0.3
      medium: 0.5
      hard: 0.2
    question_type_distribution:
      choice: 0.4
      blank: 0.3
      solution: 0.3
    total_count_range: [12, 20]
    total_score: 100
  
  exam:
    description: "期末考试：综合难度"
    difficulty_distribution:
      easy: 0.2
      medium: 0.5
      hard: 0.3
    question_type_distribution:
      choice: 0.35
      blank: 0.25
      solution: 0.4
    total_count_range: [20, 30]
    total_score: 120
  
  review:
    description: "考前复习：典型题训练"
    difficulty_distribution:
      easy: 0.2
      medium: 0.4
      hard: 0.4
    question_type_distribution:
      choice: 0.3
      blank: 0.2
      solution: 0.5
    total_count_range: [10, 20]
    total_score: 100

# 场景匹配关键词
scene_keywords:
  homework: ["作业", "练习", "巩固", "课后"]
  unit_test: ["测验", "小测", "单元", "检测"]
  exam: ["考试", "期中", "期末", "月考"]
  review: ["复习", "冲刺", "备考", "总复习"]

# 追问策略配置
followup_strategy:
  max_rounds: 3  # 最多追问 3 轮
  
  missing_subject:
    question: "请问是哪个学科的试卷？（数学/物理/化学/语文等）"
    priority: 1  # 优先级最高
  
  missing_grade:
    question: "请问是哪个年级？（初一/初二/初三/高一/高二/高三）"
    priority: 1
  
  missing_knowledge_points:
    question: |
      请问是关于哪个知识点或章节？
      您可以：
      1. 选择常见知识点（如：一元二次方程、函数、几何证明）
      2. 自由输入知识点
    priority: 2
  
  missing_scene:
    question: |
      这份试卷是用于：
      A. 课后作业（侧重基础巩固）
      B. 单元测验（全面考查）
      C. 期末考试（综合难度）
      D. 考前复习（典型题训练）
    priority: 3

# AI 生成题目配置
question_generation:
  reference_count: 3  # 从题库中选取 3 道参考题
  style_consistency: true  # 保持与题库风格一致
  
  generation_prompt_template: |
    请根据以下要求生成题目：
    
    # 知识点
    {knowledge_points}
    
    # 题型和难度
    - 题型：{question_type}
    - 难度：{difficulty}
    
    # 参考题库风格
    {reference_questions}
    
    # 生成要求
    1. 题目内容贴近生活场景
    2. 避免过于抽象，优先用具体数字
    3. 选择题选项需有迷惑性
    4. 必须提供详细解析
    5. 标注涉及的知识点

# 效果评估配置
evaluation:
  parameter_extraction:
    metrics:
      - accuracy  # 准确率
      - recall    # 召回率
      - f1_score  # F1 分数
  
  question_quality:
    criteria:
      - knowledge_point_match: 0.3   # 知识点匹配度权重
      - difficulty_accuracy: 0.2      # 难度准确性权重
      - content_quality: 0.3          # 内容质量权重
      - analysis_completeness: 0.2    # 解析完整性权重

# 调试配置
debug:
  trace_enabled: true           # 启用执行追踪
  log_level: "INFO"             # 日志级别
  save_intermediate_results: true  # 保存中间结果
```

---

### 2. Skill 加载器

**`backend/skills/loader.py`**

```python
import yaml
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ValidationError

class SkillConfig(BaseModel):
    """Skill 配置数据模型"""
    metadata: dict
    prompts: dict
    parameter_extraction: dict
    scene_strategies: dict
    scene_keywords: dict
    followup_strategy: dict
    question_generation: dict
    evaluation: dict
    debug: dict

class SkillLoader:
    """Skill 配置加载器"""
    
    def __init__(self, base_path: str = "backend/skills/definitions"):
        self.base_path = Path(base_path)
    
    def load(self, skill_name: str, version: str = "latest") -> SkillConfig:
        """
        加载指定版本的 Skill 配置
        
        Args:
            skill_name: Skill 名称（如 "exam_skill"）
            version: 版本号（如 "1.0"）或 "latest"
        
        Returns:
            SkillConfig 对象
        """
        if version == "latest":
            version = self._get_latest_version(skill_name)
        
        file_path = self.base_path / f"{skill_name}_v{version}.yaml"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Skill 配置文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        try:
            config = SkillConfig(**config_dict)
            return config
        except ValidationError as e:
            raise ValueError(f"Skill 配置格式错误: {e}")
    
    def list_versions(self, skill_name: str) -> list[str]:
        """列出所有可用版本"""
        pattern = f"{skill_name}_v*.yaml"
        files = self.base_path.glob(pattern)
        
        versions = []
        for file in files:
            # 从文件名提取版本号
            version = file.stem.split('_v')[1]
            versions.append(version)
        
        return sorted(versions, reverse=True)  # 降序排列
    
    def _get_latest_version(self, skill_name: str) -> str:
        """获取最新版本号"""
        versions = self.list_versions(skill_name)
        if not versions:
            raise ValueError(f"未找到 {skill_name} 的任何版本")
        return versions[0]
    
    def save(self, skill_name: str, version: str, config: SkillConfig):
        """保存 Skill 配置"""
        file_path = self.base_path / f"{skill_name}_v{version}.yaml"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config.dict(), f, allow_unicode=True)
    
    def validate(self, config_dict: dict) -> tuple[bool, list[str]]:
        """
        验证 Skill 配置格式
        
        Returns:
            (is_valid, error_messages)
        """
        try:
            SkillConfig(**config_dict)
            return True, []
        except ValidationError as e:
            errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            return False, errors
```

---

### 3. Skill 执行器（带追踪）

**`backend/skills/executor.py`**

```python
import time
from typing import Any, Dict
from langchain.callbacks import BaseCallbackHandler

class SkillTracer(BaseCallbackHandler):
    """Skill 执行追踪器"""
    
    def __init__(self):
        self.trace = {
            "start_time": None,
            "end_time": None,
            "steps": [],
            "llm_calls": [],
            "tool_calls": [],
            "errors": []
        }
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        self.trace["start_time"] = time.time()
    
    def on_chain_end(self, outputs, **kwargs):
        self.trace["end_time"] = time.time()
        self.trace["duration"] = self.trace["end_time"] - self.trace["start_time"]
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.trace["llm_calls"].append({
            "timestamp": time.time(),
            "prompts": prompts,
            "model": serialized.get("name")
        })
    
    def on_llm_end(self, response, **kwargs):
        if self.trace["llm_calls"]:
            self.trace["llm_calls"][-1]["response"] = response.generations[0][0].text
            self.trace["llm_calls"][-1]["tokens"] = response.llm_output.get("token_usage", {})
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        self.trace["tool_calls"].append({
            "timestamp": time.time(),
            "tool": serialized.get("name"),
            "input": input_str
        })
    
    def on_tool_end(self, output, **kwargs):
        if self.trace["tool_calls"]:
            self.trace["tool_calls"][-1]["output"] = output

class SkillExecutor:
    """Skill 执行器"""
    
    def __init__(self, skill_config: SkillConfig):
        self.config = skill_config
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Skill（无追踪）"""
        # 调用 LangGraph 执行
        result = self._run_graph(input_data, trace=False)
        return result
    
    def execute_with_trace(
        self, 
        input_data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        执行 Skill 并返回详细追踪信息
        
        Returns:
            (result, trace)
        """
        tracer = SkillTracer()
        result = self._run_graph(input_data, trace=True, callbacks=[tracer])
        return result, tracer.trace
    
    def _run_graph(self, input_data, trace=False, callbacks=None):
        """执行 LangGraph（具体实现依赖 exam_graph.py）"""
        from agents.graphs.exam_graph import create_exam_graph
        
        graph = create_exam_graph(self.config)
        
        if trace and callbacks:
            result = graph.invoke(input_data, config={"callbacks": callbacks})
        else:
            result = graph.invoke(input_data)
        
        return result
```

---

### 4. 参数提取效果评估器

**`backend/skill_debug/evaluators/parameter_evaluator.py`**

```python
from typing import Dict, List

class ParameterEvaluator:
    """参数提取效果评估器"""
    
    def evaluate(
        self, 
        extracted: Dict, 
        expected: Dict
    ) -> Dict[str, float]:
        """
        评估参数提取准确性
        
        Args:
            extracted: Agent 提取的参数
            expected: 期望的参数（标准答案）
        
        Returns:
            {
                "accuracy": 0.85,      # 准确率
                "recall": 0.90,         # 召回率
                "f1_score": 0.87,       # F1 分数
                "field_scores": {       # 每个字段的得分
                    "subject": 1.0,
                    "grade": 1.0,
                    "knowledge_points": 0.67
                }
            }
        """
        scores = {}
        
        # 1. 计算每个字段的得分
        field_scores = {}
        for field in expected.keys():
            field_scores[field] = self._compare_field(
                extracted.get(field), 
                expected[field]
            )
        
        # 2. 计算总体指标
        correct_count = sum(1 for score in field_scores.values() if score == 1.0)
        total_count = len(expected)
        
        accuracy = correct_count / total_count if total_count > 0 else 0
        
        extracted_count = len([k for k in extracted.keys() if extracted[k]])
        recall = correct_count / extracted_count if extracted_count > 0 else 0
        
        f1_score = 2 * (accuracy * recall) / (accuracy + recall) if (accuracy + recall) > 0 else 0
        
        return {
            "accuracy": accuracy,
            "recall": recall,
            "f1_score": f1_score,
            "field_scores": field_scores
        }
    
    def _compare_field(self, extracted_value, expected_value) -> float:
        """比较单个字段，返回 0-1 的得分"""
        if extracted_value == expected_value:
            return 1.0
        
        # 数组类型特殊处理（知识点列表）
        if isinstance(expected_value, list):
            if not isinstance(extracted_value, list):
                return 0.0
            
            # 计算交集占比
            expected_set = set(expected_value)
            extracted_set = set(extracted_value)
            
            intersection = expected_set & extracted_set
            union = expected_set | extracted_set
            
            return len(intersection) / len(union) if union else 0.0
        
        # 字符串类型模糊匹配
        if isinstance(expected_value, str) and isinstance(extracted_value, str):
            if expected_value.lower() in extracted_value.lower() or \
               extracted_value.lower() in expected_value.lower():
                return 0.8  # 部分匹配
        
        return 0.0
    
    def batch_evaluate(
        self, 
        test_cases: List[Dict]
    ) -> Dict[str, Any]:
        """
        批量评估测试用例
        
        Args:
            test_cases: [
                {
                    "id": "case_001",
                    "input": "用户输入...",
                    "extracted": {...},  # Agent 提取结果
                    "expected": {...}    # 期望结果
                }
            ]
        
        Returns:
            {
                "overall_accuracy": 0.85,
                "overall_f1": 0.87,
                "case_results": [
                    {"id": "case_001", "accuracy": 0.9, ...}
                ],
                "failed_cases": [...]  # 失败的用例
            }
        """
        results = []
        
        for case in test_cases:
            result = self.evaluate(case["extracted"], case["expected"])
            result["id"] = case["id"]
            result["input"] = case["input"]
            results.append(result)
        
        # 统计总体指标
        overall_accuracy = sum(r["accuracy"] for r in results) / len(results)
        overall_f1 = sum(r["f1_score"] for r in results) / len(results)
        
        # 找出失败的用例（F1 < 0.7）
        failed_cases = [r for r in results if r["f1_score"] < 0.7]
        
        return {
            "overall_accuracy": overall_accuracy,
            "overall_f1": overall_f1,
            "total_cases": len(test_cases),
            "passed_cases": len(test_cases) - len(failed_cases),
            "failed_cases": failed_cases,
            "case_results": results
        }
```

---

### 5. Skill 调试 API

**`backend/skill_debug/api/playground.py`**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from skills.loader import SkillLoader
from skills.executor import SkillExecutor

router = APIRouter(prefix="/skill-debug", tags=["Skill 调试"])

class PlaygroundRequest(BaseModel):
    skill_name: str
    skill_version: str
    input_data: dict
    enable_trace: bool = True

class PlaygroundResponse(BaseModel):
    result: dict
    trace: dict = None
    execution_time: float

@router.post("/playground/execute")
async def execute_skill(request: PlaygroundRequest):
    """
    Skill 测试场：单次执行
    
    用于教研人员快速测试某个输入下的 Skill 执行效果
    """
    try:
        # 1. 加载 Skill 配置
        loader = SkillLoader()
        skill_config = loader.load(request.skill_name, request.skill_version)
        
        # 2. 执行 Skill
        executor = SkillExecutor(skill_config)
        
        if request.enable_trace:
            result, trace = executor.execute_with_trace(request.input_data)
            return PlaygroundResponse(
                result=result,
                trace=trace,
                execution_time=trace["duration"]
            )
        else:
            result = executor.execute(request.input_data)
            return PlaygroundResponse(
                result=result,
                execution_time=0
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playground/batch-test")
async def batch_test_skill(
    skill_name: str,
    skill_version: str,
    test_case_file: str
):
    """
    批量测试：用测试用例集验证 Skill 效果
    
    Args:
        skill_name: Skill 名称
        skill_version: 版本号
        test_case_file: 测试用例文件路径（如 "parameter_extraction/cases.json"）
    
    Returns:
        评估报告（准确率、召回率、失败用例等）
    """
    from skill_debug.evaluators.parameter_evaluator import ParameterEvaluator
    import json
    
    # 1. 加载测试用例
    with open(f"backend/skill_debug/test_cases/{test_case_file}", 'r') as f:
        test_cases = json.load(f)
    
    # 2. 加载 Skill 并执行
    loader = SkillLoader()
    skill_config = loader.load(skill_name, skill_version)
    executor = SkillExecutor(skill_config)
    
    # 3. 批量执行
    for case in test_cases:
        result = executor.execute({"messages": [{"role": "user", "content": case["input"]}]})
        case["extracted"] = result.get("extracted_params", {})
    
    # 4. 评估效果
    evaluator = ParameterEvaluator()
    evaluation_report = evaluator.batch_evaluate(test_cases)
    
    # 5. 保存报告
    report_path = f"backend/skill_debug/reports/{skill_name}_v{skill_version}_batch_test.json"
    with open(report_path, 'w') as f:
        json.dump(evaluation_report, f, ensure_ascii=False, indent=2)
    
    return evaluation_report


@router.post("/playground/ab-test")
async def ab_test_skills(
    skill_name: str,
    version_a: str,
    version_b: str,
    test_case_file: str
):
    """
    A/B 测试：对比两个 Skill 版本的效果
    
    Returns:
        {
            "version_a_metrics": {...},
            "version_b_metrics": {...},
            "improvement": {
                "accuracy": +0.05,
                "f1_score": +0.03
            },
            "recommendation": "version_b"  # 推荐版本
        }
    """
    # 分别测试两个版本
    report_a = await batch_test_skill(skill_name, version_a, test_case_file)
    report_b = await batch_test_skill(skill_name, version_b, test_case_file)
    
    # 计算改进幅度
    improvement = {
        "accuracy": report_b["overall_accuracy"] - report_a["overall_accuracy"],
        "f1_score": report_b["overall_f1"] - report_a["overall_f1"]
    }
    
    # 推荐版本
    recommendation = version_b if improvement["f1_score"] > 0 else version_a
    
    return {
        "version_a_metrics": report_a,
        "version_b_metrics": report_b,
        "improvement": improvement,
        "recommendation": recommendation
    }
```

---

### 6. Skill 调试 Web 界面（伪代码）

**Playground 页面功能**：

```typescript
// skill-debug-ui/src/pages/playground.tsx

export default function SkillPlayground() {
  const [skillVersion, setSkillVersion] = useState('1.0');
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);
  const [trace, setTrace] = useState(null);

  const executeSkill = async () => {
    const response = await fetch('/api/skill-debug/playground/execute', {
      method: 'POST',
      body: JSON.stringify({
        skill_name: 'exam_skill',
        skill_version: skillVersion,
        input_data: { messages: [{ role: 'user', content: inputText }] },
        enable_trace: true
      })
    });
    
    const data = await response.json();
    setResult(data.result);
    setTrace(data.trace);
  };

  return (
    <div>
      {/* 版本选择器 */}
      <SkillVersionSelector value={skillVersion} onChange={setSkillVersion} />
      
      {/* 输入区 */}
      <textarea 
        placeholder="输入测试对话..." 
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      
      <button onClick={executeSkill}>执行 Skill</button>
      
      {/* 结果展示 */}
      <div className="result-panel">
        <h3>提取参数</h3>
        <JsonViewer data={result?.extracted_params} />
        
        <h3>执行追踪</h3>
        <TraceViewer trace={trace} />
        {/* 展示：
          - 每个节点的执行时间
          - LLM 调用次数和 token 消耗
          - 工具调用记录
        */}
      </div>
    </div>
  );
}
```

---

## 核心价值

### 1. **教研人员自主迭代**
- 修改 YAML 配置即可调整规则（无需改代码）
- 可视化界面友好，降低技术门槛

### 2. **数据驱动优化**
- 自动统计准确率、召回率等指标
- A/B 测试对比不同版本效果
- 失败用例自动收集，针对性优化

### 3. **快速验证迭代**
- 单次测试：立即看到效果
- 批量测试：全面验证 Skill 质量
- 版本管理：随时回滚到历史版本

### 4. **执行过程透明**
- Trace 记录每个节点的执行详情
- LLM 调用和 token 消耗可视化
- 方便定位问题和优化 Prompt

---

## 使用流程示例

### 场景：教研人员想优化"场景匹配"策略

**步骤 1**：修改 Skill 配置
```yaml
# exam_skill_v1.1.yaml
scene_keywords:
  homework: ["作业", "练习", "巩固", "课后", "预习"]  # 新增"预习"
  unit_test: ["测验", "小测", "单元", "检测", "周测"]  # 新增"周测"
```

**步骤 2**：在 Playground 快速测试
- 输入："帮我出份预习题"
- 查看是否识别为 `homework` 场景

**步骤 3**：批量测试验证
- 运行 50 个测试用例
- 查看准确率是否提升

**步骤 4**：A/B 测试对比
- 对比 v1.0 vs v1.1
- 如果 F1 提升 > 3%，则发布 v1.1

**步骤 5**：线上灰度
- 10% 流量使用 v1.1
- 监控实际效果
- 全量发布或回滚

---

## 下一步

这个 Skill 调试模块设计好后，我可以：

1. **创建目录结构**（`skills/`, `skill_debug/`）
2. **实现 Skill 加载器**（支持 YAML 加载和验证）
3. **实现参数评估器**（计算准确率、F1）
4. **搭建调试 API**（Playground、批量测试、A/B 测试）
5. **准备测试用例库**（50 个标准用例）

你觉得这个方案如何？有需要调整的地方吗？