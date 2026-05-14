"""
相似题生成命令行工具
快速验证：上传题目图片 → 生成3道相似题
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from workflows.similar_question_workflow import create_similar_question_workflow
from workflows.similar_question_workflow.state import SimilarQuestionWorkflowState

# 加载环境变量
load_dotenv()


async def generate_similar_questions(image_path: str):
    """
    基于图片生成相似题

    Args:
        image_path: 题目图片路径
    """
    print("=" * 80)
    print("🎯 相似题生成工具")
    print("=" * 80)

    # 检查图片文件
    if not os.path.exists(image_path):
        print(f"\n❌ 图片文件不存在：{image_path}")
        return

    print(f"\n📸 输入图片：{image_path}")
    print(f"   文件大小：{os.path.getsize(image_path) / 1024:.2f} KB")

    # 创建工作流
    workflow = create_similar_question_workflow()

    # 初始化状态
    initial_state: SimilarQuestionWorkflowState = {
        "image_path": image_path,
        "ocr_result": {},
        "similar_questions": [],
        "validation_results": [],
        "retry_count": 0,
        "error": None
    }

    print("\n⏳ 正在处理...")
    print("   1️⃣  OCR 识别原题...")

    # 执行工作流
    try:
        final_state = await workflow.ainvoke(initial_state)

        if final_state.get("error"):
            print(f"\n❌ 生成失败：{final_state['error']}")
            return

        # 显示 OCR 结果
        ocr_result = final_state.get("ocr_result", {})
        print(f"   ✅ OCR 识别完成（{len(ocr_result.get('question', ''))} 字）")
        print("   2️⃣  生成相似题...")
        print("   3️⃣  校验题目...")
        print("   4️⃣  格式化输出...")

        # 显示原题
        print(f"\n{'=' * 80}")
        print("📝 原题内容")
        print(f"{'=' * 80}")
        print(ocr_result.get('question', ''))

        # 显示相似题
        similar_questions = final_state.get("similar_questions", [])

        print(f"\n{'=' * 80}")
        print(f"🎯 生成相似题（共 {len(similar_questions)} 道）")
        print(f"{'=' * 80}")

        for i, question in enumerate(similar_questions, 1):
            print(f"\n{'─' * 80}")
            print(f"📌 相似题 {i}")
            print(f"{'─' * 80}")

            print(f"\n题目：")
            print(f"{question.get('question', '')}")

            print(f"\n答案：{question.get('answer', '')}")

            if question.get('explanation'):
                print(f"\n解析：")
                print(f"{question.get('explanation', '')}")

        # 统计信息
        validation_results = final_state.get("validation_results", [])
        valid_count = sum(1 for r in validation_results if r["valid"])

        print(f"\n{'=' * 80}")
        print(f"✅ 生成完成：{valid_count}/{len(validation_results)} 道题目通过校验")
        print(f"{'=' * 80}")

    except Exception as e:
        print(f"\n❌ 执行异常：{e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python scripts/generate_similar_question.py <图片路径>")
        print("\n示例：")
        print("  python scripts/generate_similar_question.py test_images/math_question_1.png")
        print("  python scripts/generate_similar_question.py ~/Desktop/my_question.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    asyncio.run(generate_similar_questions(image_path))


if __name__ == "__main__":
    main()
