"""
测试 LLM 连接

用法：
python scripts/test_llm_connection.py
"""

import sys
import os
import asyncio

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.llm_service import LLMService, LLMProvider

# 加载环境变量
load_dotenv()


async def test_llm(provider: str = "deepseek"):
    """
    测试 LLM 连接

    Args:
        provider: LLM 提供商（deepseek/kimi/claude/qwen）
    """
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} LLM 连接")
    print(f"{'='*60}\n")

    try:
        # 1. 初始化服务
        print(f"✓ 正在初始化 {provider} 服务...")
        llm = LLMService(provider=provider)
        print(f"✓ {provider} 服务初始化成功\n")

        # 2. 测试简单对话
        print("测试 1: 简单对话")
        print("-" * 60)
        test_message = "你好，请用一句话介绍你自己。"
        print(f"用户: {test_message}")

        messages = [{"role": "user", "content": test_message}]

        response = await llm.chat(messages=messages, stream=False)
        print(f"助手: {response.content}\n")
        print("✓ 简单对话测试通过\n")

        # 3. 测试参数提取（模拟）
        print("测试 2: 参数提取")
        print("-" * 60)
        conversation = [
            {"role": "user", "content": "帮我出份初二数学试卷"}
        ]

        system_prompt = """
请从对话中提取以下参数，以 JSON 格式返回：
- subject: 学科
- grade: 年级
- knowledge_points: 知识点列表（如果有）

如果某个参数缺失，设为 null。
"""

        response = await llm.chat(
            messages=conversation,
            system_prompt=system_prompt,
            stream=False
        )

        print(f"提取结果: {response.content}\n")
        print("✓ 参数提取测试通过\n")

        # 4. 测试流式输出
        print("测试 3: 流式输出")
        print("-" * 60)
        print("用户: 请讲一个关于数学的小故事")
        print("助手: ", end="", flush=True)

        messages = [{"role": "user", "content": "请讲一个关于数学的小故事（50字以内）"}]

        stream_generator = await llm.chat(messages=messages, stream=True)
        async for chunk in stream_generator:
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end="", flush=True)

        print("\n\n✓ 流式输出测试通过\n")

        print(f"{'='*60}")
        print(f"✅ {provider.upper()} 所有测试通过！")
        print(f"{'='*60}\n")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_all_providers():
    """测试所有配置的 LLM 提供商"""
    providers = []

    # 检查哪些提供商配置了 API Key
    if os.getenv("DEEPSEEK_API_KEY") and os.getenv("DEEPSEEK_API_KEY") != "sk-your-deepseek-key":
        providers.append("deepseek")

    if os.getenv("KIMI_API_KEY") and os.getenv("KIMI_API_KEY") != "sk-your-kimi-key":
        providers.append("kimi")

    if os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "sk-ant-your-claude-key":
        providers.append("claude")

    if os.getenv("QWEN_API_KEY") and os.getenv("QWEN_API_KEY") != "sk-your-qwen-key":
        providers.append("qwen")

    if not providers:
        print("\n⚠️  未检测到任何已配置的 LLM 提供商")
        print("请编辑 .env 文件，填入至少一个 API Key\n")
        return

    print(f"\n检测到已配置的提供商: {', '.join(providers)}\n")

    results = {}
    for provider in providers:
        success = await test_llm(provider)
        results[provider] = success

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for provider, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{provider.ljust(10)}: {status}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # 检查是否指定了特定提供商
    if len(sys.argv) > 1:
        provider = sys.argv[1].lower()
        if provider not in ["deepseek", "kimi", "claude", "qwen"]:
            print(f"❌ 不支持的提供商: {provider}")
            print("支持的提供商: deepseek, kimi, claude, qwen")
            sys.exit(1)

        asyncio.run(test_llm(provider))
    else:
        # 测试所有配置的提供商
        asyncio.run(test_all_providers())
