"""
相似题生成 API 测试脚本
使用 requests 直接测试 FastAPI 路由
"""
import sys
from pathlib import Path
import asyncio

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_similar_questions():
    """测试生成相似题 API"""
    print("=" * 60)
    print("测试：POST /api/similar-question/generate")
    print("=" * 60)

    # 查找测试图片
    test_images_dir = backend_dir / "test_images"
    image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))

    if not image_files:
        print("❌ 未找到测试图片")
        return

    test_image = image_files[0]
    print(f"\n📸 测试图片：{test_image.name}")

    # 发送请求
    with open(test_image, "rb") as f:
        response = client.post(
            "/api/similar-question/generate",
            files={"image": (test_image.name, f, "image/png")},
            params={"count": 3}
        )

    # 检查响应
    print(f"\n📊 响应状态：{response.status_code}")

    if response.status_code == 200:
        data = response.json()

        print(f"\n✅ 生成成功")
        print(f"   - 耗时：{data['generation_time']} 秒")
        print(f"   - 题目数量：{data['question_count']}")

        # OCR 结果
        ocr_result = data["ocr_result"]
        print(f"\n📝 OCR 识别结果：")
        print(f"   - 题目长度：{len(ocr_result['question'])} 字")
        print(f"   - 题目内容（前100字）：{ocr_result['question'][:100]}")

        # 相似题
        print(f"\n🎯 生成的相似题：")
        for i, question in enumerate(data["similar_questions"], 1):
            print(f"\n   --- 题目 {i} ---")
            print(f"   题目：{question.get('question', '')[:80]}...")
            print(f"   答案：{question.get('answer', '')}")

            # 校验结果
            validation = data["validation_results"][i - 1]
            status = "✅ 通过" if validation["valid"] else "❌ 失败"
            print(f"   校验：{status}")
            if validation["errors"]:
                print(f"   错误：{', '.join(validation['errors'])}")

        # 统计校验结果
        valid_count = sum(1 for v in data["validation_results"] if v["valid"])
        print(f"\n📊 校验统计：{valid_count}/{data['question_count']} 通过")

    else:
        print(f"\n❌ 请求失败")
        print(f"错误信息：{response.json()}")


def test_regenerate_single_question():
    """测试重新生成单道题 API"""
    print("\n" + "=" * 60)
    print("测试：POST /api/similar-question/regenerate")
    print("=" * 60)

    original_question = """
一个分数的分子扩大到原来的3倍，分母缩小到原来的 1/3，这个分数就()
A.不变 B.扩大到原来的6倍 C.扩大到原来的9倍 D.缩小到原来的1/9
    """.strip()

    print(f"\n📝 原题：{original_question[:50]}...")

    # 发送请求
    response = client.post(
        "/api/similar-question/regenerate",
        json={
            "original_question": original_question,
            "question_index": 1
        }
    )

    print(f"\n📊 响应状态：{response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 重新生成成功")
        print(f"   题目：{data.get('question', '')[:80]}...")
        print(f"   答案：{data.get('answer', '')}")
        print(f"   校验：{'✅ 通过' if data.get('valid') else '❌ 失败'}")
    else:
        print(f"\n❌ 请求失败")
        print(f"错误信息：{response.json()}")


def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("测试：GET /health")
    print("=" * 60)

    response = client.get("/health")
    print(f"\n📊 响应状态：{response.status_code}")
    print(f"响应内容：{response.json()}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 相似题生成 API 测试")
    print("=" * 60)

    # 1. 健康检查
    test_health_check()

    # 2. 生成相似题
    test_generate_similar_questions()

    # 3. 重新生成单道题
    test_regenerate_single_question()

    print("\n" + "=" * 60)
    print("🎉 测试完成")
    print("=" * 60)
