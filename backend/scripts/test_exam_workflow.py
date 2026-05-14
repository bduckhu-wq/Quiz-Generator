"""
测试完整的 ExamWorkflow

用法：
python scripts/test_exam_workflow.py
"""

import sys
import os
import asyncio
import json

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService

# 加载环境变量
load_dotenv()


async def test_complete_workflow():
    """测试完整的出题流程（参数完整的情况）"""

    print("\n" + "="*60)
    print("测试场景 1: 参数完整的出题请求")
    print("="*60 + "\n")

    # 1. 准备输入
    user_input = "帮我出一份初二数学关于一元二次方程的试卷"
    session_id = "test_session_001"

    # 2. 加载 Skill
    print("加载 Skill...")
    loader = SkillLoader()
    llm = LLMService(provider="deepseek")
    skill_context = await loader.route_to_skill(user_input, llm)
    print(f"✓ 已加载 Skill（{len(skill_context)} 字符）\n")

    # 3. 创建初始状态
    print("创建初始状态...")
    initial_state = create_initial_state(
        user_input=user_input,
        session_id=session_id,
        skill_context=skill_context,
        messages=[]
    )
    print("✓ 初始状态创建完成\n")

    # 4. 执行 Workflow
    print("执行 Workflow...")
    print("-" * 60)

    workflow = get_workflow()

    try:
        result = await workflow.ainvoke(initial_state)

        # 5. 分析结果
        print("\n" + "-" * 60)
        print("Workflow 执行完成！")
        print("=" * 60)

        # 检查是否需要追问
        if result.get("needs_followup"):
            print("\n❌ 参数不完整，需要追问")
            print(f"追问消息: {result['followup_message']}")
            print(f"缺失参数: {', '.join(result['missing_params'])}")
            return False

        # 检查试卷
        final_exam = result.get("final_exam")
        if not final_exam:
            print("\n❌ 未生成试卷")
            return False

        # 显示试卷信息
        print("\n✅ 试卷生成成功！")
        print("\n试卷信息:")
        print(f"  • 试卷 ID: {final_exam['exam_id']}")
        print(f"  • 学科: {final_exam['subject']}")
        print(f"  • 年级: {final_exam['grade']}")
        print(f"  • 知识点: {', '.join(final_exam['knowledge_points'])}")
        print(f"  • 场景: {final_exam['scene']}")
        print(f"  • 题目数量: {final_exam['question_count']} 道")
        print(f"  • 总分: {final_exam['total_score']} 分")

        print("\n题目来源:")
        print(f"  • 题库: {final_exam['source_stats']['database']} 道")
        print(f"  • AI 生成: {final_exam['source_stats']['ai_generated']} 道")

        # 显示题目列表（前 5 道）
        print("\n题目列表（前5道）:")
        for q in final_exam['questions'][:5]:
            print(f"  {q['index']}. [{q['question_type']}] {q['content'][:40]}... ({q['score']}分)")

        # 显示执行追踪
        print("\n执行追踪:")
        for trace in result["execution_trace"]:
            step_name = trace["step"]
            duration = trace.get("duration", 0)
            print(f"  • {step_name}: {duration:.2f}s")

        total_time = sum(t.get("duration", 0) for t in result["execution_trace"])
        print(f"\n总耗时: {total_time:.2f}s")

        return True

    except Exception as e:
        print(f"\n❌ Workflow 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_incomplete_workflow():
    """测试参数不完整的场景（需要追问）"""

    print("\n" + "="*60)
    print("测试场景 2: 参数不完整，需要追问")
    print("="*60 + "\n")

    # 1. 准备输入（故意缺少年级）
    user_input = "帮我出份数学试卷"
    session_id = "test_session_002"

    # 2. 加载 Skill
    print("加载 Skill...")
    loader = SkillLoader()
    llm = LLMService(provider="deepseek")
    skill_context = await loader.route_to_skill(user_input, llm)
    print(f"✓ 已加载 Skill\n")

    # 3. 创建初始状态
    initial_state = create_initial_state(
        user_input=user_input,
        session_id=session_id,
        skill_context=skill_context,
        messages=[]
    )

    # 4. 执行 Workflow
    print("执行 Workflow...")
    print("-" * 60)

    workflow = get_workflow()

    try:
        result = await workflow.ainvoke(initial_state)

        print("\n" + "-" * 60)
        print("Workflow 执行完成！")
        print("=" * 60)

        # 检查是否需要追问
        if result.get("needs_followup"):
            print("\n✅ 正确触发追问流程")
            print(f"\n追问消息:")
            print(f"  {result['followup_message']}")
            print(f"\n缺失参数: {', '.join(result['missing_params'])}")

            # 显示提取的参数
            print(f"\n已提取参数:")
            for key, value in result["extracted_params"].items():
                print(f"  • {key}: {value}")

            return True
        else:
            print("\n❌ 应该触发追问但没有")
            return False

    except Exception as e:
        print(f"\n❌ Workflow 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""

    print("\n" + "="*60)
    print("ExamWorkflow 端到端测试")
    print("="*60)

    results = {}

    # 测试 1: 参数完整
    results["complete"] = await test_complete_workflow()

    print("\n" + "="*60)
    print()

    # 测试 2: 参数不完整
    results["incomplete"] = await test_incomplete_workflow()

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  • {test_name}: {status}")

    print("="*60)

    if all_passed:
        print("\n✅ 所有测试通过！ExamWorkflow 工作正常")
    else:
        print("\n⚠️  部分测试未通过")

    print()


if __name__ == "__main__":
    asyncio.run(main())
