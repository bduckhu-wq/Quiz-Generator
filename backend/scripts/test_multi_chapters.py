"""
测试多个章节的出题能力
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService


async def test_chapter(user_input, test_name):
    """测试单个场景"""
    print("\n" + "="*70)
    print(f"测试场景: {test_name}")
    print("="*70)
    print(f"输入: {user_input}\n")

    loader = SkillLoader()
    llm = LLMService(provider='deepseek')
    skill_context = await loader.route_to_skill(user_input, llm)

    workflow = get_workflow()
    initial_state = create_initial_state(
        user_input=user_input,
        session_id=f'test_{test_name}',
        skill_context=skill_context,
        messages=[]
    )

    result = await workflow.ainvoke(initial_state)

    # 显示结果
    if result.get('needs_followup'):
        print(f"❌ 需要追问: {result['followup_message']}")
    else:
        exam = result.get('final_exam')
        if exam:
            print("✅ 试卷生成成功")
            print(f"  学科: {exam['subject']}")
            print(f"  年级: {exam['grade']}")
            print(f"  章节: {', '.join(exam['knowledge_points'])}")
            print(f"  场景: {exam['scene']}")
            print(f"  题目数量: {exam['question_count']} 道")
            print(f"  总分: {exam['total_score']} 分")
            print(f"  来源: 题库{exam['source_stats']['database']}道 + AI生成{exam['source_stats']['ai_generated']}道")

            # 显示前3题
            print("\n  题目预览:")
            for q in exam['questions'][:3]:
                print(f"    {q['index']}. [{q['question_type']}] {q['content'][:40]}...")

            # 显示耗时
            total_time = sum(t['duration'] for t in result['execution_trace'])
            print(f"\n  总耗时: {total_time:.2f}秒")
        else:
            print("❌ 生成失败")


async def test_all():
    """测试多个场景"""
    print("\n" + "#"*70)
    print("# 三年级数学多章节出题测试")
    print("#"*70)

    test_cases = [
        ("三年级数学第一章乘法10道题", "第一章_乘法"),
        ("三年级数学第二章除法8题", "第二章_除法"),
        ("三年级数学第四章长度单位测验", "第四章_长度"),
        ("三年级数学第五章面积6道题", "第五章_面积"),
        ("三年级数学第七章分数初步5题", "第七章_分数"),
    ]

    for user_input, test_name in test_cases:
        await test_chapter(user_input, test_name)
        await asyncio.sleep(1)  # 避免频繁调用LLM

    print("\n" + "#"*70)
    print("# 测试完成")
    print("#"*70)


if __name__ == "__main__":
    asyncio.run(test_all())
