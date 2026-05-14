import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService

async def check_allocation():
    user_input = '三年级数学下学期第三章第二节课后练习5题'

    loader = SkillLoader()
    llm = LLMService(provider='deepseek')
    skill_context = await loader.route_to_skill(user_input, llm)

    workflow = get_workflow()
    initial_state = create_initial_state(
        user_input=user_input,
        session_id='test',
        skill_context=skill_context,
        messages=[]
    )

    result = await workflow.ainvoke(initial_state)

    print('用户指定题量:', result['extracted_params'].get('question_count'))
    print('场景配置题量:', result['scene_config']['total_count'])
    print('题目分配:', result['allocation'])
    print('缺口分析:', result['gap_breakdown'])
    print('总缺口:', result['gap'])
    print('实际生成:', len(result['generated_questions']))

asyncio.run(check_allocation())
