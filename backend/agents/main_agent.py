"""
MainAgent - 主 Agent（融合 OpenClaw Skill + LangGraph Workflow）
"""

from typing import Dict, Any
from skills.loader import SkillLoader
from workflows.exam_workflow import get_workflow as get_exam_workflow


class MainAgent:
    """
    主 Agent - 融合两种模式：
    1. OpenClaw 模式：Skill 文档指导 LLM（策略层）
    2. LangGraph 模式：Workflow 确定性执行（执行层）

    职责：
    - 渐进式加载相关 Skill
    - 路由到对应的 Workflow
    - 执行 Workflow 并返回结果
    """

    def __init__(self):
        self.skill_loader = SkillLoader()
        self.workflows = {
            "exam": get_exam_workflow(),
            # "search": get_search_workflow(),
            # "adapt": get_adapt_workflow()
        }

    async def execute(
        self,
        user_input: str,
        session_id: str,
        messages: list = None
    ) -> Dict[str, Any]:
        """
        执行用户请求

        Args:
            user_input: 用户输入
            session_id: 会话 ID
            messages: 对话历史（可选）

        Returns:
            {
                "result": {...},        # Workflow 执行结果
                "needs_followup": bool, # 是否需要追问
                "followup_message": str # 追问消息
            }
        """
        # 1. 渐进式加载相关 Skill
        skill_context = self.skill_loader.load_relevant_skills(
            user_input,
            max_skills=2  # 最多加载 2 个 Skill
        )

        # 2. 路由到 Workflow（目前简化为直接调用 exam）
        workflow_name = self._route_to_workflow(user_input)

        # 3. 获取 Workflow
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {
                "error": f"Workflow '{workflow_name}' not found",
                "needs_followup": False
            }

        # 4. 构建初始状态
        from workflows.exam_workflow.state import create_initial_state
        initial_state = create_initial_state(
            user_input=user_input,
            session_id=session_id,
            skill_context=skill_context,
            messages=messages or []
        )

        # 5. 执行 Workflow
        result = await workflow.ainvoke(initial_state)

        # 6. 返回结果
        return {
            "result": result.get("final_exam"),
            "needs_followup": result.get("needs_followup", False),
            "followup_message": result.get("followup_message"),
            "execution_trace": result.get("execution_trace", [])
        }

    def _route_to_workflow(self, user_input: str) -> str:
        """
        路由到对应的 Workflow

        简化版：基于关键词匹配
        完整版：调用 LLM 决策

        Args:
            user_input: 用户输入

        Returns:
            workflow_name: "exam" / "search" / "adapt"
        """
        # 简化实现：关键词匹配
        if any(keyword in user_input for keyword in ["出题", "生成试卷", "组卷", "create exam"]):
            return "exam"
        elif any(keyword in user_input for keyword in ["搜题", "查找题目", "search"]):
            return "search"
        elif any(keyword in user_input for keyword in ["改编", "调整难度", "adapt"]):
            return "adapt"
        else:
            # 默认返回 exam
            return "exam"

    async def execute_with_stream(
        self,
        user_input: str,
        session_id: str,
        messages: list = None
    ):
        """
        流式执行（支持 SSE）

        Yields:
            {"type": "thinking", "content": "..."}
            {"type": "progress", "step": "...", "progress": 0.5}
            {"type": "result", "data": {...}}
        """
        # TODO: 实现流式输出
        # 使用 LangGraph 的 astream_events() 方法
        pass


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = MainAgent()

        # 测试出题
        result = await agent.execute(
            user_input="帮我出份初二数学单元测验",
            session_id="test_session_001"
        )

        print("执行结果:")
        print(f"需要追问: {result['needs_followup']}")
        if result['needs_followup']:
            print(f"追问消息: {result['followup_message']}")
        else:
            print(f"试卷: {result['result']}")

    asyncio.run(main())
