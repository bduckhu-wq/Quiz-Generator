"""
测试 LLM 驱动的 Skill 路由

用法：
python scripts/test_llm_routing.py
"""

import sys
import os
import asyncio

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from skills.loader import SkillLoader
from services.llm_service import LLMService

# 加载环境变量
load_dotenv()


async def test_llm_routing():
    """测试 LLM 驱动的 Skill 路由功能"""

    print("\n" + "="*60)
    print("测试 LLM 驱动的 Skill 路由")
    print("="*60 + "\n")

    # 1. 初始化
    print("初始化 SkillLoader 和 LLMService...")
    loader = SkillLoader()
    llm = LLMService(provider="deepseek")
    print("✓ 初始化成功\n")

    # 2. 测试各种用户输入
    test_cases = [
        {
            "input": "出3道题",
            "expected": "exam_skill",
            "description": "简短出题请求（无关键词精确匹配）"
        },
        {
            "input": "随便搜搜",
            "expected": "search_skill",
            "description": "口语化搜题请求"
        },
        {
            "input": "帮我找几个数学问题",
            "expected": "search_skill",
            "description": "委婉表达搜题意图"
        },
        {
            "input": "来份初二物理卷子",
            "expected": "exam_skill",
            "description": "口语化出题请求"
        },
        {
            "input": "你好，今天天气怎么样？",
            "expected": "none",
            "description": "闲聊（不应触发 Skill）"
        },
        {
            "input": "生成一份期末考试试卷",
            "expected": "exam_skill",
            "description": "标准出题请求"
        },
        {
            "input": "我想要一些关于函数的题目",
            "expected": "search_skill",
            "description": "知识点相关搜题"
        }
    ]

    results = []

    print("测试 LLM 路由效果")
    print("-" * 60)

    for idx, case in enumerate(test_cases, 1):
        print(f"\n测试 {idx}/{len(test_cases)}: {case['description']}")
        print(f"  用户输入: \"{case['input']}\"")
        print(f"  预期: {case['expected']}")

        try:
            # 调用 LLM 路由
            skill_content = await loader.route_to_skill(case["input"], llm)

            # 判断结果
            if case["expected"] == "none":
                actual = "none" if not skill_content else "matched"
            else:
                if f'name="{case["expected"]}"' in skill_content:
                    actual = case["expected"]
                else:
                    actual = "none" if not skill_content else "unknown"

            # 判断是否通过
            passed = (actual == case["expected"])
            status = "✓" if passed else "❌"

            print(f"  实际: {actual}")
            print(f"  {status} {'通过' if passed else '失败'}")

            results.append({
                "case": case["description"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": actual,
                "passed": passed
            })

        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            results.append({
                "case": case["description"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": "error",
                "passed": False
            })

    # 3. 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)\n")

    print("详细结果:")
    for r in results:
        status = "✓" if r["passed"] else "❌"
        print(f"  {status} {r['case']}")
        if not r["passed"]:
            print(f"      输入: {r['input']}")
            print(f"      预期: {r['expected']}, 实际: {r['actual']}")

    if passed_count == total_count:
        print("\n" + "="*60)
        print("✅ 所有测试通过！LLM 路由工作正常")
        print("="*60 + "\n")
        return True
    else:
        print("\n" + "="*60)
        print(f"⚠️  {total_count - passed_count} 个测试未通过")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_llm_routing())
    sys.exit(0 if success else 1)
