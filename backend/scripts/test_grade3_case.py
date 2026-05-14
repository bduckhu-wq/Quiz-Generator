"""
测试三年级数学案例

测试内容：三年级数学下学期第三章第二节课后练习5题
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService


async def test_grade3():
    print('='*60)
    print('测试输入: 三年级数学下学期第三章第二节课后练习5题')
    print('='*60 + '\n')

    user_input = '三年级数学下学期第三章第二节课后练习5题'

    # 1. LLM智能路由
    print('【步骤1: LLM路由识别】')
    loader = SkillLoader()
    llm = LLMService(provider='deepseek')

    skill_context = await loader.route_to_skill(user_input, llm)

    if skill_context:
        print('✓ 成功路由到出题Skill\n')
    else:
        print('✗ 路由失败\n')
        return

    # 2. 执行Workflow
    print('【步骤2: 执行出题流程】')
    workflow = get_workflow()
    initial_state = create_initial_state(
        user_input=user_input,
        session_id='test_grade3',
        skill_context=skill_context,
        messages=[]
    )

    result = await workflow.ainvoke(initial_state)

    # 3. 分析结果
    print('\n【步骤3: 结果分析】')
    print('-'*60)

    if result.get('needs_followup'):
        print('状态: 需要追问')
        print(f'追问内容: {result["followup_message"]}')
        print(f'\n缺失参数: {result.get("missing_params", [])}')
    else:
        final_exam = result.get('final_exam')
        if final_exam:
            print('状态: ✓ 试卷生成成功')
            print(f'  学科: {final_exam["subject"]}')
            print(f'  年级: {final_exam["grade"]}')
            print(f'  知识点: {final_exam.get("knowledge_points", [])}')
            print(f'  场景: {final_exam["scene"]}')
            print(f'  题目数量: {final_exam["question_count"]} 道')
            print(f'  总分: {final_exam["total_score"]} 分')
            print(f'  来源统计:')
            print(f'    - 题库: {final_exam["source_stats"]["database"]} 道')
            print(f'    - AI生成: {final_exam["source_stats"]["ai_generated"]} 道')

            # 显示题目详情
            if final_exam["question_count"] > 0:
                print('\n  题目列表:')
                for q in final_exam["questions"][:3]:  # 只显示前3题
                    print(f'    {q["index"]}. [{q["question_type"]}] {q["content"][:30]}...')
        else:
            print('状态: ✗ 生成失败')

    # 4. 提取的参数
    print('\n【步骤4: 参数提取详情】')
    print('-'*60)
    extracted = result.get('extracted_params', {})
    print(f'学科: {extracted.get("subject")}')
    print(f'年级: {extracted.get("grade")}')
    print(f'知识点: {extracted.get("knowledge_points")}')
    print(f'场景: {extracted.get("scene")}')
    print(f'题目数量: {extracted.get("question_count")}')
    print(f'\n完整参数: {extracted}')

    # 5. 执行追踪
    print('\n【步骤5: 执行追踪】')
    print('-'*60)
    for trace in result.get('execution_trace', []):
        step = trace.get('step')
        duration = trace.get('duration', 0)
        print(f'{step}: {duration:.2f}s')

    total_time = sum(t.get('duration', 0) for t in result.get('execution_trace', []))
    print(f'\n总耗时: {total_time:.2f}s')

    print('\n' + '='*60)
    print('测试完成')
    print('='*60)


if __name__ == "__main__":
    asyncio.run(test_grade3())
