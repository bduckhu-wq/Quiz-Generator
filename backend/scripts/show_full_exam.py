"""
展示完整试卷内容
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService


async def show_exam():
    print('='*70)
    print('三年级数学下学期第三章第二节课后练习 - 完整试卷')
    print('='*70 + '\n')

    user_input = '三年级数学下学期第三章第二节课后练习5题'

    loader = SkillLoader()
    llm = LLMService(provider='deepseek')
    skill_context = await loader.route_to_skill(user_input, llm)

    workflow = get_workflow()
    initial_state = create_initial_state(
        user_input=user_input,
        session_id='demo',
        skill_context=skill_context,
        messages=[]
    )

    result = await workflow.ainvoke(initial_state)
    exam = result['final_exam']

    # 试卷头
    print(f"学科：{exam['subject']}")
    print(f"年级：{exam['grade']}")
    print(f"章节：{', '.join(exam['knowledge_points'])}")
    print(f"场景：{exam['scene']}（课后练习）")
    print(f"总分：{exam['total_score']}分")
    print(f"题目数量：{exam['question_count']}道")
    print(f"来源：题库{exam['source_stats']['database']}道 + AI生成{exam['source_stats']['ai_generated']}道")
    print('\n' + '='*70 + '\n')

    # 题目详情
    for q in exam['questions']:
        print(f"【第{q['index']}题】 {q['question_type']} | 难度：{q['difficulty']} | {q['score']}分")
        print(f"\n{q['content']}\n")

        if q.get('options'):
            options = json.loads(q['options']) if isinstance(q['options'], str) else q['options']
            for opt in options:
                print(f"  {opt}")
            print()

        print(f"答案：{q['answer']}")

        if q.get('analysis'):
            print(f"解析：{q['analysis']}")

        if q.get('knowledge_points'):
            kps = json.loads(q['knowledge_points']) if isinstance(q['knowledge_points'], str) else q['knowledge_points']
            print(f"知识点：{', '.join(kps)}")

        print('\n' + '-'*70 + '\n')

    # 性能统计
    print('='*70)
    print('性能统计')
    print('='*70)
    for trace in result['execution_trace']:
        print(f"{trace['step']}: {trace['duration']:.2f}秒")

    total_time = sum(t['duration'] for t in result['execution_trace'])
    print(f"\n总耗时：{total_time:.2f}秒")


if __name__ == "__main__":
    asyncio.run(show_exam())
