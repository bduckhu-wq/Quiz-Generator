"""
相似题生成工作流测试脚本
验证 4 节点工作流能否正常运行
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
import logging

# 加载环境变量
load_dotenv()

# 配置日志输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


async def test_workflow():
    """测试相似题生成工作流"""
    print("=" * 60)
    print("相似题生成工作流测试")
    print("=" * 60)

    # 1. 检查环境变量
    if not os.getenv("ALIYUN_ACCESS_KEY_ID"):
        print("\n❌ 错误：未设置 ALIYUN_ACCESS_KEY_ID 环境变量")
        return

    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\n❌ 错误：未设置 DEEPSEEK_API_KEY 环境变量")
        return

    print("\n✅ 环境变量配置正常")

    # 2. 查找测试图片
    test_images_dir = backend_dir / "test_images"
    image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))

    if not image_files:
        print(f"\n⚠️  未找到测试图片")
        print(f"请将测试图片（.jpg/.png）放入目录：{test_images_dir}")
        return

    test_image = str(image_files[0])
    print(f"\n📸 测试图片：{os.path.basename(test_image)}")

    # 3. 创建工作流
    try:
        workflow = create_similar_question_workflow()
        print("✅ 工作流创建成功")
    except Exception as e:
        print(f"❌ 工作流创建失败：{e}")
        return

    # 4. 运行工作流
    print(f"\n{'=' * 60}")
    print("开始执行工作流")
    print(f"{'=' * 60}")

    initial_state: SimilarQuestionWorkflowState = {
        "image_path": test_image,
        "question_count": 3,  # 默认生成3道（可动态调整）
        "ocr_result": {},
        "similar_questions": [],
        "validation_results": [],
        "retry_count": 0,
        "error": None
    }

    try:
        # 执行工作流
        final_state = await workflow.ainvoke(initial_state)

        # 5. 输出结果
        print(f"\n{'=' * 60}")
        print("工作流执行结果")
        print(f"{'=' * 60}")

        if final_state.get("error"):
            print(f"\n❌ 执行失败：{final_state['error']}")
            return

        # OCR 结果
        ocr_result = final_state.get("ocr_result", {})
        print(f"\n📝 OCR 识别结果：")
        print(f"   题目长度：{len(ocr_result.get('question', ''))} 字")
        print(f"   题目内容（前 100 字）：")
        print(f"   {ocr_result.get('question', '')[:100]}")

        # 相似题结果
        similar_questions = final_state.get("similar_questions", [])
        print(f"\n🎯 生成相似题数量：{len(similar_questions)} 道")

        for i, question in enumerate(similar_questions, 1):
            print(f"\n--- 相似题 {i} ---")
            print(f"题目：{question.get('question', '')[:80]}...")
            print(f"答案：{question.get('answer', '')}")
            print(f"推断学科：{question.get('inferred_subject', '')}")
            print(f"推断年级：{question.get('inferred_grade', '')}")
            print(f"知识点：{', '.join(question.get('inferred_knowledge_points', []))}")

        # 校验结果
        validation_results = final_state.get("validation_results", [])
        valid_count = sum(1 for r in validation_results if r["valid"])
        print(f"\n✅ 校验通过：{valid_count}/{len(validation_results)} 道")

        print(f"\n{'=' * 60}")
        print("🎉 工作流测试完成！")
        print(f"{'=' * 60}")

    except Exception as e:
        print(f"\n❌ 工作流执行异常：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow())
