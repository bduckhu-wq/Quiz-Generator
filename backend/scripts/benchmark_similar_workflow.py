"""
相似题生成性能基准测试
分析各环节耗时
"""
import sys
import os
import asyncio
import time
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from services.aliyun_ocr_service import AliyunOCRService
from services.llm_service import LLMService
from pathlib import Path
import json
import re

# 加载环境变量
load_dotenv()

# 加载 Skill
SKILL_PATH = backend_dir / "skills" / "similar-question-generation" / "SKILL.md"
SKILL_CONTENT = SKILL_PATH.read_text(encoding="utf-8")


async def benchmark():
    """性能基准测试"""
    print("=" * 80)
    print("相似题生成性能基准测试")
    print("=" * 80)

    image_path = str(backend_dir / "test_images" / "math_question_1.png")

    # 1. OCR 识别
    print("\n⏱️  环节 1：OCR 识别")
    start = time.time()
    ocr_service = AliyunOCRService()
    ocr_result = await ocr_service.recognize_question(image_path)
    ocr_time = time.time() - start
    print(f"   耗时：{ocr_time:.2f} 秒")
    print(f"   识别字符数：{len(ocr_result['question'])} 字")

    # 2. 构建 System Prompt
    print("\n⏱️  环节 2：构建 System Prompt")
    start = time.time()

    system_prompt = f"""你是一个专业的数学题目生成助手。请严格按照以下 Skill 定义生成相似题。

{SKILL_CONTENT}

**输出要求**：
1. 必须严格遵守四层控制模型（核心层不变，结构层≤10%，表达层30-50%，数值层80-100%）
2. 相似度精确控制在 70%
3. 干扰项必须来自真实误解，不能硬塞无关约束
4. 输出格式必须为 JSON，格式如下：

```json
{{
  "similar_questions": [
    {{
      "question": "题目内容（保留 LaTeX 公式格式）",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（如 A/B/C/D）",
      "analysis": "详细解析",
      "inferred_subject": "推断的学科",
      "inferred_grade": "推断的年级",
      "inferred_knowledge_points": ["知识点1", "知识点2"]
    }}
  ]
}}
```

**重要**：只返回 JSON，不要有任何额外文字。"""

    user_message = f"""请基于以下原题生成 3 道相似题（70%相似度）：

**原题内容：**
{ocr_result['question']}

请严格按照 Skill 定义生成，确保：
1. 核心层不变（知识点、数学模型、解题逻辑）
2. 结构层至少改变 1 处（设问角度、求解对象等）
3. 场景完全陌生化（不能只改数字）
4. 干扰项来自真实误解

输出 JSON 格式。"""

    prompt_time = time.time() - start
    print(f"   耗时：{prompt_time:.2f} 秒")
    print(f"   System Prompt 字符数：{len(system_prompt):,}")
    print(f"   User Message 字符数：{len(user_message):,}")
    print(f"   总输入字符数：{len(system_prompt) + len(user_message):,}")
    print(f"   估算输入 Token 数：{int((len(system_prompt) + len(user_message)) * 1.5):,}")

    # 3. LLM 调用
    print("\n⏱️  环节 3：LLM 生成相似题")
    start = time.time()

    llm = LLMService(provider="deepseek")
    response = await llm.chat(
        messages=[{"role": "user", "content": user_message}],
        system_prompt=system_prompt,
        stream=False
    )

    llm_time = time.time() - start
    print(f"   耗时：{llm_time:.2f} 秒")
    print(f"   输出字符数：{len(response.content):,}")
    print(f"   估算输出 Token 数：{int(len(response.content) * 1.5):,}")

    # 4. JSON 解析
    print("\n⏱️  环节 4：JSON 解析")
    start = time.time()

    content = response.content.strip()
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group(0))
        similar_questions = result.get("similar_questions", [])

    parse_time = time.time() - start
    print(f"   耗时：{parse_time:.2f} 秒")
    print(f"   生成题目数：{len(similar_questions)} 道")

    # 总结
    total_time = ocr_time + prompt_time + llm_time + parse_time
    print(f"\n{'=' * 80}")
    print("性能统计")
    print(f"{'=' * 80}")
    print(f"  OCR 识别：{ocr_time:.2f} 秒 ({ocr_time/total_time*100:.1f}%)")
    print(f"  构建 Prompt：{prompt_time:.2f} 秒 ({prompt_time/total_time*100:.1f}%)")
    print(f"  LLM 生成：{llm_time:.2f} 秒 ({llm_time/total_time*100:.1f}%)")
    print(f"  JSON 解析：{parse_time:.2f} 秒 ({parse_time/total_time*100:.1f}%)")
    print(f"  总耗时：{total_time:.2f} 秒")
    print(f"\n  输入 Token：~{int((len(system_prompt) + len(user_message)) * 1.5):,}")
    print(f"  输出 Token：~{int(len(response.content) * 1.5):,}")
    print(f"  生成速度：~{int(len(response.content) * 1.5 / llm_time):.0f} tokens/秒")

    # 优化建议
    print(f"\n{'=' * 80}")
    print("⚡ 优化建议")
    print(f"{'=' * 80}")

    if llm_time / total_time > 0.9:
        print("  ⚠️  瓶颈在 LLM 生成（占总时间 >90%）")
        print("  建议：")
        print("    1. 精简 Skill 定义（当前 9KB，可优化到 3-4KB）")
        print("    2. 使用流式输出（stream=True）提升用户体验")
        print("    3. 考虑并行生成（3 道题分 3 次调用）")
        print("    4. 使用更快的模型（如 deepseek-chat 而非 deepseek-v4-pro）")


if __name__ == "__main__":
    asyncio.run(benchmark())
