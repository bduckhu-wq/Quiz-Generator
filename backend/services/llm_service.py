"""
LLM 服务 - 统一封装多个 LLM 提供商
"""

import os
import sys
from enum import Enum
from typing import List, Dict, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# 添加 utils 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.retry import retry_async, LLMError

# 尝试从配置导入，如果失败则直接使用 os.getenv
try:
    from app.config.settings import get_llm_api_key
except ImportError:
    def get_llm_api_key(provider: str) -> str:
        key_map = {
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "kimi": os.getenv("KIMI_API_KEY"),
            "claude": os.getenv("ANTHROPIC_API_KEY"),
            "qwen": os.getenv("QWEN_API_KEY"),
            "doubao": os.getenv("DOUBAO_API_KEY")
        }
        return key_map.get(provider)


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""
    DEEPSEEK = "deepseek"
    KIMI = "kimi"
    CLAUDE = "claude"
    QWEN = "qwen"
    DOUBAO = "doubao"


class LLMService:
    """
    LLM 调用服务

    功能：
    1. 支持多个 LLM 提供商（DeepSeek / Kimi / Claude / 通义千问）
    2. 统一的调用接口
    3. 支持流式和非流式输出
    4. 支持 Tool Calling
    """

    def __init__(self, provider: str = None):
        # 如果未指定 provider，从环境变量读取
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.provider = LLMProvider(provider)
        self.client = self._init_client(self.provider)

    def _init_client(self, provider: LLMProvider):
        """
        初始化 LLM 客户端

        Args:
            provider: LLM 提供商

        Returns:
            LangChain ChatModel 实例
        """
        if provider == LLMProvider.DEEPSEEK:
            api_key = get_llm_api_key("deepseek") or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment")

            base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
            model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

            return ChatOpenAI(
                base_url=base_url,
                api_key=api_key,
                model=model,
                streaming=True,
                temperature=temperature
            )

        elif provider == LLMProvider.KIMI:
            api_key = get_llm_api_key("kimi") or os.getenv("KIMI_API_KEY")
            if not api_key:
                raise ValueError("KIMI_API_KEY not found in environment")
            return ChatOpenAI(
                base_url="https://api.moonshot.cn/v1",
                api_key=api_key,
                model="moonshot-v1-128k",
                streaming=True,
                temperature=0.7
            )

        elif provider == LLMProvider.CLAUDE:
            api_key = get_llm_api_key("claude") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            return ChatAnthropic(
                api_key=api_key,
                model="claude-3-5-sonnet-20241022",
                streaming=True,
                temperature=0.7
            )

        elif provider == LLMProvider.QWEN:
            api_key = get_llm_api_key("qwen") or os.getenv("QWEN_API_KEY")
            if not api_key:
                raise ValueError("QWEN_API_KEY not found in environment")
            return ChatOpenAI(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=api_key,
                model="qwen-max",
                streaming=True,
                temperature=0.7
            )

        elif provider == LLMProvider.DOUBAO:
            api_key = get_llm_api_key("doubao") or os.getenv("DOUBAO_API_KEY")
            if not api_key:
                raise ValueError("DOUBAO_API_KEY not found in environment")

            base_url = os.getenv("DOUBAO_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
            model = os.getenv("DOUBAO_MODEL", "doubao-seed-2-0-mini-260428")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

            return ChatOpenAI(
                base_url=base_url,
                api_key=api_key,
                model=model,
                streaming=True,
                temperature=temperature
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @retry_async(max_retries=3, delay=1.0, exceptions=(Exception,))
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        stream: bool = False
    ):
        """
        统一的 LLM 调用接口

        Args:
            messages: 对话历史 [{"role": "user", "content": "..."}]
            system_prompt: 系统 Prompt（可选）
            tools: 工具定义（可选）
            stream: 是否流式输出

        Returns:
            非流式：完整响应
            流式：AsyncGenerator
        """
        # 构建完整 messages
        full_messages = []

        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})

        full_messages.extend(messages)

        # 调用 LLM（避免传递 None 作为 tools）
        if stream:
            # 流式返回 AsyncGenerator
            return self._chat_stream(full_messages, tools)
        else:
            # 非流式返回完整响应
            if tools:
                return await self.client.ainvoke(full_messages, tools=tools)
            else:
                return await self.client.ainvoke(full_messages)

    async def _chat_stream(self, messages: List, tools: Optional[List[Dict]] = None):
        """内部流式处理方法"""
        if tools:
            async for chunk in self.client.astream(messages, tools=tools):
                yield chunk
        else:
            async for chunk in self.client.astream(messages):
                yield chunk

    async def extract_parameters(
        self,
        messages: List[Dict[str, str]],
        skill_context: str
    ) -> Dict:
        """
        从对话中提取参数

        Args:
            messages: 对话历史
            skill_context: Skill 策略文档

        Returns:
            提取的参数字典
        """
        system_prompt = f"""
你是一个专业的参数提取助手。

{skill_context}

请从以下对话中提取结构化参数，以 JSON 格式返回。
"""

        # 调用 LLM
        response = await self.chat(
            messages=messages,
            system_prompt=system_prompt,
            stream=False
        )

        # 解析响应
        # TODO: 从响应中提取 JSON
        extracted_params = {}

        return extracted_params

    async def generate_followup(
        self,
        missing_params: List[str],
        skill_context: str
    ) -> str:
        """
        生成追问消息

        Args:
            missing_params: 缺失的参数列表
            skill_context: Skill 策略文档

        Returns:
            追问消息文本
        """
        system_prompt = f"""
你是一个专业的出题助手。

{skill_context}

用户缺失以下参数：{', '.join(missing_params)}

请生成一个友好的追问，引导用户补充这些信息。
追问要简洁、清晰，提供常见选项。
"""

        response = await self.chat(
            messages=[{"role": "user", "content": "请生成追问"}],
            system_prompt=system_prompt,
            stream=False
        )

        return response.content

    async def generate_questions(
        self,
        knowledge_points: List[str],
        difficulty: str,
        question_type: str,
        count: int,
        reference_questions: List[Dict] = None
    ) -> List[Dict]:
        """
        AI 生成题目

        Args:
            knowledge_points: 知识点列表
            difficulty: 难度（easy/medium/hard）
            question_type: 题型（choice/blank/solution）
            count: 生成数量
            reference_questions: 参考题库风格（可选）

        Returns:
            生成的题目列表
        """
        system_prompt = f"""
你是一个专业的 K12 出题专家。

请根据以下要求生成题目：
- 知识点：{', '.join(knowledge_points)}
- 难度：{difficulty}
- 题型：{question_type}
- 数量：{count}

如果提供了参考题目，请参考其语言风格和结构。

输出格式：JSON 数组
"""

        # TODO: 调用 LLM 生成
        generated_questions = []

        return generated_questions


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def main():
        # 测试 LLM 服务
        llm = LLMService(provider="deepseek")

        messages = [
            {"role": "user", "content": "帮我出份初二数学试卷"}
        ]

        response = await llm.chat(messages)
        print(f"LLM 响应: {response.content}")

    asyncio.run(main())
