"""
ExamWorkflow 节点函数

每个节点是一个独立的处理函数：
- 接收 State
- 执行逻辑（可能调用 LLM、工具、其他 Workflow）
- 更新 State
- 返回更新后的 State
"""

import time
import json
import re
import uuid
from typing import Dict, List
from .state import ExamWorkflowState
from services.llm_service import LLMService
from services.question_service import QuestionService
from models.base import SessionLocal
from models import Subject, Grade, QuestionType, Difficulty
from utils.question_validator import QuestionValidator


# ========== 辅助函数 ==========

def add_trace(state: ExamWorkflowState, step: str, duration: float, result: Dict = None):
    """
    添加执行追踪记录（避免 LangGraph state 累积问题）

    Args:
        state: 当前状态
        step: 步骤名称
        duration: 执行时长
        result: 执行结果（可选）
    """
    new_trace = state.get("execution_trace", []).copy()
    trace_entry = {
        "step": step,
        "timestamp": time.time(),
        "duration": duration
    }
    if result is not None:
        trace_entry["result"] = result

    new_trace.append(trace_entry)
    state["execution_trace"] = new_trace


# ========== 节点 1: 提取参数 ==========

async def extract_parameters(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    从对话历史中提取结构化参数

    流程：
    1. 构建 Prompt（包含 Skill 策略）
    2. 调用 LLM 提取参数
    3. 更新 state["extracted_params"]
    """
    start_time = time.time()

    # 初始化 LLM 服务
    llm = LLMService(provider="deepseek")

    # 构建提取 Prompt
    system_prompt = f"""你是一个参数提取助手。

{state["skill_context"]}

**任务**：从用户对话中提取出题参数。

**输出格式**（必须严格 JSON）：
{{
    "subject": "学科名称（数学/物理/化学等）",
    "grade": "年级（一年级/二年级/三年级/四年级/五年级/六年级/初一/初二/初三/高一/高二/高三）",
    "knowledge_points": ["知识点1", "知识点2"],
    "scene": "场景（homework/unit_test/exam/review，如果未明确指定则为 null）",
    "question_count": 数字（如果用户明确指定题目数量，如"5题"、"10道题"）
}}

**特别注意**：
- 年级识别：
  * "三年级" → "三年级"（小学）
  * "初三" → "初三"（初中）
  * 不要混淆"三年级"和"初三"
- 章节信息处理：
  * "第三章第二节" → knowledge_points: ["第三章第二节"]
  * "下学期第三章" → knowledge_points: ["第三章"]
  * 保留完整的章节路径信息
- 题目数量：
  * "5题" → question_count: 5
  * "10道题" → question_count: 10
  * 如果未明确指定，设为 null
- 场景识别：
  * "课后练习" → scene: "homework"
  * "单元测验" → scene: "unit_test"
- 如果某个参数缺失，设为 null
- 只返回 JSON，不要有其他文字"""

    # 调用 LLM
    messages = state["messages"] + [{"role": "user", "content": state["user_input"]}]
    response = await llm.chat(
        messages=messages,
        system_prompt=system_prompt,
        stream=False
    )

    # 解析 JSON
    try:
        content = response.content.strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            extracted = json.loads(json_match.group(0))
        else:
            extracted = {}
    except Exception as e:
        print(f"⚠️  参数提取失败: {e}")
        extracted = {}

    # 更新状态
    state["extracted_params"] = extracted
    state["current_step"] = "extract_parameters"
    add_trace(state, "extract_parameters", time.time() - start_time, extracted)

    return state


# ========== 节点 2: 检查参数完整性 ==========

async def check_completeness(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    检查参数是否完整

    必需参数：subject, grade, knowledge_points
    """
    start_time = time.time()

    params = state["extracted_params"]
    required_fields = ["subject", "grade", "knowledge_points"]

    # 检查缺失
    missing = []
    for field in required_fields:
        if not params.get(field):
            missing.append(field)

    # 更新状态
    state["is_params_complete"] = len(missing) == 0
    state["missing_params"] = missing
    state["current_step"] = "check_completeness"
    add_trace(state, "check_completeness", time.time() - start_time,
              {"is_complete": state["is_params_complete"], "missing": missing})

    return state


# ========== 节点 3: 生成追问 ==========

async def generate_followup(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    生成追问消息（参数不完整时）

    根据 Skill 策略生成友好的追问
    """
    start_time = time.time()

    missing = state["missing_params"]
    llm = LLMService(provider="deepseek")

    # 构建追问 Prompt
    system_prompt = f"""你是一个友好的出题助手。

{state["skill_context"]}

**任务**：用户缺失以下参数：{', '.join(missing)}

生成一个友好、简洁的追问，引导用户补充。
- 不要太生硬
- 可以给出常见选项示例
- 一次只问一个参数
- 不超过 50 字"""

    response = await llm.chat(
        messages=[{"role": "user", "content": "请生成追问"}],
        system_prompt=system_prompt,
        stream=False
    )

    followup_message = response.content.strip()

    # 更新状态
    state["needs_followup"] = True
    state["followup_message"] = followup_message
    state["current_step"] = "generate_followup"
    add_trace(state, "generate_followup", time.time() - start_time)

    return state


# ========== 节点 4: 匹配场景策略 ==========

async def match_scene_strategy(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    匹配场景策略（基于 Skill 配置）

    流程：
    1. 读取 Skill 中的场景策略表
    2. 根据关键词或明确指定匹配场景
    3. 返回场景配置（难度分布、题型分布、题量）
    """
    start_time = time.time()

    # TODO: 从 Skill 配置加载场景策略
    # from skills.loader import SkillLoader
    # skill_config = SkillLoader().load_skill_config("exam_skill")
    # scene_strategies = skill_config["scene_strategies"]

    # 模拟场景策略（开发时用）
    scene_strategies = {
        "homework": {
            "difficulty_distribution": {"easy": 0.5, "medium": 0.4, "hard": 0.1},
            "question_type_distribution": {"choice": 0.3, "blank": 0.4, "solution": 0.3},
            "total_count": 12,
            "total_score": 100
        },
        "unit_test": {
            "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
            "question_type_distribution": {"choice": 0.4, "blank": 0.3, "solution": 0.3},
            "total_count": 15,
            "total_score": 100
        }
    }

    # 确定场景
    scene = state["extracted_params"].get("scene") or "unit_test"  # 默认单元测验
    scene_config = scene_strategies.get(scene, scene_strategies["unit_test"]).copy()
    scene_config["scene"] = scene

    # 如果用户明确指定题目数量，覆盖场景默认值
    user_question_count = state["extracted_params"].get("question_count")
    if user_question_count and isinstance(user_question_count, int):
        scene_config["total_count"] = user_question_count

    # 更新状态
    state["scene_config"] = scene_config
    state["current_step"] = "match_scene_strategy"
    add_trace(state, "match_scene_strategy", time.time() - start_time, {"scene": scene})

    return state


# ========== 节点 5: 计算题目分配 ==========

async def calculate_allocation(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    计算题目分配方案

    根据场景配置计算每种（题型 + 难度）的题目数量
    优化：确保总题量不超过用户指定
    """
    start_time = time.time()

    scene_config = state["scene_config"]
    total_count = scene_config["total_count"]
    type_dist = scene_config["question_type_distribution"]
    diff_dist = scene_config["difficulty_distribution"]

    allocation = {}
    allocated_total = 0

    # 第一轮：按比例分配（不强制至少1题）
    for qtype, type_ratio in type_dist.items():
        type_count = round(total_count * type_ratio)
        allocation[qtype] = {}

        for difficulty, diff_ratio in diff_dist.items():
            count = round(type_count * diff_ratio)
            allocation[qtype][difficulty] = count
            allocated_total += count

    # 调整分配，确保总数严格等于 total_count
    allocated_total = sum(sum(d.values()) for d in allocation.values())

    # 如果总数超过限制，优先削减困难题
    if allocated_total > total_count:
        overflow = allocated_total - total_count
        # 按优先级削减：困难 > 中等 > 简单
        for difficulty in ["hard", "medium", "easy"]:
            if overflow == 0:
                break
            for qtype in allocation.keys():
                if overflow == 0:
                    break
                if allocation[qtype].get(difficulty, 0) > 0:
                    reduce = min(allocation[qtype][difficulty], overflow)
                    allocation[qtype][difficulty] -= reduce
                    overflow -= reduce

    # 如果总数不足，优先增加简单题
    elif allocated_total < total_count:
        shortage = total_count - allocated_total
        for difficulty in ["easy", "medium", "hard"]:
            if shortage == 0:
                break
            for qtype in allocation.keys():
                if shortage == 0:
                    break
                allocation[qtype][difficulty] = allocation[qtype].get(difficulty, 0) + 1
                shortage -= 1

    # 最终验证：确保总数等于 total_count
    final_total = sum(sum(d.values()) for d in allocation.values())
    if final_total != total_count:
        print(f"⚠️  警告：分配总数({final_total})与目标({total_count})不一致")

    # 更新状态
    state["allocation"] = allocation
    state["current_step"] = "calculate_allocation"
    add_trace(state, "calculate_allocation", time.time() - start_time, allocation)

    return state


# ========== 节点 6: 搜题 ==========

async def search_questions(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    调用搜题服务（数据库检索）

    根据知识点、学科、年级、题型、难度搜索题目
    """
    start_time = time.time()

    # 初始化数据库服务
    db = SessionLocal()
    service = QuestionService(db)

    try:
        # 提取参数
        params = state["extracted_params"]
        allocation = state["allocation"]

        # 转换枚举类型
        subject = Subject(params["subject"])
        grade = Grade(params["grade"])
        knowledge_points = params.get("knowledge_points", [])

        # 按分配方案搜索题目
        search_results = []

        for qtype, diff_breakdown in allocation.items():
            # 映射题型
            qtype_enum = _map_question_type(qtype)

            for difficulty, count in diff_breakdown.items():
                if count == 0:
                    continue

                # 转换难度（映射英文到中文枚举值）
                diff_map = {
                    "easy": Difficulty.EASY,  # "简单"
                    "medium": Difficulty.MEDIUM,  # "中等"
                    "hard": Difficulty.HARD  # "困难"
                }
                diff_enum = diff_map.get(difficulty)

                # 搜索题目
                questions = service.search(
                    subject=subject,
                    grade=grade,
                    question_types=[qtype_enum] if qtype_enum else None,
                    difficulties=[diff_enum],
                    knowledge_points=knowledge_points if knowledge_points else None,
                    limit=count
                )

                # 转为字典
                for q in questions:
                    search_results.append(q.to_dict())

        # 更新状态
        state["search_results"] = search_results
        state["current_step"] = "search_questions"
        add_trace(state, "search_questions", time.time() - start_time,
                  {"found_count": len(search_results)})

    finally:
        db.close()

    return state


def _map_question_type(qtype: str) -> QuestionType:
    """映射题型名称到枚举"""
    mapping = {
        "choice": QuestionType.SINGLE_CHOICE,
        "blank": QuestionType.BLANK,
        "solution": QuestionType.SOLUTION,
        "calculation": QuestionType.CALCULATION,
        "proof": QuestionType.PROOF
    }
    return mapping.get(qtype)


# ========== 节点 7: 分析缺口 ==========

async def analyze_gap(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    分析题目缺口

    计算需要 AI 生成的题目数量
    """
    start_time = time.time()

    allocation = state["allocation"]
    search_results = state["search_results"]

    # 统计已搜到的题目
    found_count = {}
    for q in search_results:
        qtype = q["question_type"]
        difficulty = q["difficulty"]

        # 映射回分配方案的键
        qtype_key = _reverse_map_question_type(qtype)
        diff_key = difficulty.lower() if difficulty != "中等" else "medium"

        if qtype_key not in found_count:
            found_count[qtype_key] = {}
        found_count[qtype_key][diff_key] = found_count[qtype_key].get(diff_key, 0) + 1

    # 计算缺口
    gap_breakdown = {}
    total_gap = 0

    for qtype, diff_breakdown in allocation.items():
        gap_breakdown[qtype] = {}
        for difficulty, needed in diff_breakdown.items():
            found = found_count.get(qtype, {}).get(difficulty, 0)
            gap = max(0, needed - found)
            gap_breakdown[qtype][difficulty] = gap
            total_gap += gap

    # 更新状态
    state["gap"] = total_gap
    state["gap_breakdown"] = gap_breakdown
    state["current_step"] = "analyze_gap"
    add_trace(state, "analyze_gap", time.time() - start_time,
              {"gap": total_gap, "breakdown": gap_breakdown})

    return state


def _reverse_map_question_type(qtype_name: str) -> str:
    """反向映射题型"""
    mapping = {
        "单选题": "choice",
        "填空题": "blank",
        "解答题": "solution",
        "计算题": "calculation",
        "证明题": "proof"
    }
    return mapping.get(qtype_name, "solution")


# ========== 节点 8: AI 生成题目 ==========

async def generate_questions(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    AI 批量生成题目（补充缺口）

    策略：
    1. 按缺口breakdown逐个题型生成
    2. 提供参考题目风格
    3. 质量校验后返回
    """
    start_time = time.time()

    gap = state.get("gap", 0)

    if gap == 0:
        state["generated_questions"] = []
        state["current_step"] = "generate_questions"
        add_trace(state, "generate_questions", time.time() - start_time,
                  {"generated_count": 0, "gap": 0})
        return state

    # 初始化服务
    llm = LLMService(provider="deepseek")
    validator = QuestionValidator()

    # 获取参数
    params = state["extracted_params"]
    subject = params["subject"]
    grade = params["grade"]
    knowledge_points = params.get("knowledge_points", [])
    gap_breakdown = state["gap_breakdown"]
    search_results = state["search_results"]

    # 提取参考题目风格
    reference_style = ""
    if search_results:
        sample_q = search_results[0]
        reference_style = f"""
参考题目风格示例：
题型：{sample_q['question_type']}
内容：{sample_q['content']}
答案：{sample_q['answer']}
"""

    generated = []

    # 按题型生成
    for qtype, diff_breakdown in gap_breakdown.items():
        for difficulty, count in diff_breakdown.items():
            if count == 0:
                continue

            # 构建生成Prompt
            system_prompt = f"""你是一个专业的K12出题专家。

请为以下需求生成题目：

**基础信息**
- 学科：{subject}
- 年级：{grade}
- 知识点：{', '.join(knowledge_points) if knowledge_points else '无特定知识点'}
- 题型：{qtype}（{_get_qtype_chinese(qtype)}）
- 难度：{difficulty}（{_get_difficulty_chinese(difficulty)}）
- 数量：{count} 道

{reference_style}

**输出格式**（严格JSON数组）：
[
  {{
    "question_type": "{_get_qtype_chinese(qtype)}",
    "difficulty": "{_get_difficulty_chinese(difficulty)}",
    "content": "题目内容",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "正确答案",
    "analysis": "答案解析",
    "knowledge_points": ["知识点1", "知识点2"]
  }}
]

**要求**：
1. 题目内容符合{grade}学生认知水平
2. 选择题必须有4个选项（A/B/C/D）
3. 填空题options设为null
4. 答案必须准确
5. 解析简洁清晰
6. 只返回JSON数组，不要其他文字
"""

            try:
                response = await llm.chat(
                    messages=[{"role": "user", "content": f"请生成{count}道题目"}],
                    system_prompt=system_prompt,
                    stream=False
                )

                # 解析JSON
                content = response.content.strip()
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    questions_data = json.loads(json_match.group(0))

                    # 质量校验
                    for q_data in questions_data:
                        # 补充字段
                        q_data["subject"] = subject
                        q_data["grade"] = grade
                        q_data["score"] = _get_default_score(qtype, difficulty)
                        q_data["source"] = "AI生成"
                        q_data["id"] = str(uuid.uuid4())

                        # 校验
                        is_valid, error = validator.validate_question(q_data)
                        if is_valid:
                            generated.append(q_data)
                        else:
                            print(f"⚠️  生成题目校验失败: {error}")

            except Exception as e:
                print(f"⚠️  AI生成失败 ({qtype}/{difficulty}): {e}")
                continue

    # 更新状态
    state["generated_questions"] = generated
    state["current_step"] = "generate_questions"
    add_trace(state, "generate_questions", time.time() - start_time,
              {"generated_count": len(generated), "gap": gap})

    return state


def _get_qtype_chinese(qtype: str) -> str:
    """获取题型中文名"""
    mapping = {
        "choice": "单选题",
        "blank": "填空题",
        "solution": "解答题",
        "calculation": "计算题",
        "proof": "证明题"
    }
    return mapping.get(qtype, "解答题")


def _get_difficulty_chinese(difficulty: str) -> str:
    """获取难度中文名"""
    mapping = {
        "easy": "简单",
        "medium": "中等",
        "hard": "困难"
    }
    return mapping.get(difficulty, "中等")


def _get_default_score(qtype: str, difficulty: str) -> int:
    """根据题型和难度返回默认分值"""
    base_scores = {
        "choice": 5,
        "blank": 6,
        "solution": 10,
        "calculation": 8,
        "proof": 12
    }
    difficulty_multiplier = {
        "easy": 1.0,
        "medium": 1.2,
        "hard": 1.5
    }

    base = base_scores.get(qtype, 5)
    multiplier = difficulty_multiplier.get(difficulty, 1.0)

    return int(base * multiplier)


async def assemble_exam(state: ExamWorkflowState) -> ExamWorkflowState:
    """
    组装最终试卷

    合并题库题目和 AI 生成题目，排序，分配题号
    """
    start_time = time.time()

    # 合并题目（添加来源标记）
    db_questions = state["search_results"]
    ai_questions = state["generated_questions"]

    # 为题库题目添加来源标记
    for q in db_questions:
        q["source"] = "题库"

    # 为AI生成题目添加来源标记（如果还没有）
    for q in ai_questions:
        if "source" not in q or q["source"] == "AI生成":
            q["source"] = "AI生成"

    all_questions = db_questions + ai_questions

    # 按题型排序（选择题 → 填空题 → 解答题）
    type_order = ["单选题", "多选题", "填空题", "计算题", "证明题", "解答题"]

    def sort_key(q):
        qtype = q["question_type"]
        return type_order.index(qtype) if qtype in type_order else 99

    all_questions.sort(key=sort_key)

    # 严格按照用户指定的题目数量截取
    user_question_count = state["extracted_params"].get("question_count")
    if user_question_count and isinstance(user_question_count, int):
        all_questions = all_questions[:user_question_count]

    # 分配题号和分数
    for idx, q in enumerate(all_questions, 1):
        q["index"] = idx
        if "score" not in q:
            q["score"] = q.get("default_score", 5)

    # 计算总分
    total_score = sum(q["score"] for q in all_questions)

    # 统计来源
    db_count = len(state["search_results"])
    ai_count = len(state["generated_questions"])

    # 构建试卷
    final_exam = {
        "exam_id": str(uuid.uuid4()),
        "subject": state["extracted_params"]["subject"],
        "grade": state["extracted_params"]["grade"],
        "knowledge_points": state["extracted_params"].get("knowledge_points", []),
        "scene": state["scene_config"]["scene"],
        "questions": all_questions,
        "total_score": total_score,
        "question_count": len(all_questions),
        "source_stats": {
            "database": db_count,
            "ai_generated": ai_count
        },
        "created_at": time.time()
    }

    # 更新状态
    state["final_exam"] = final_exam
    state["needs_followup"] = False
    state["current_step"] = "assemble_exam"
    add_trace(state, "assemble_exam", time.time() - start_time)

    return state
