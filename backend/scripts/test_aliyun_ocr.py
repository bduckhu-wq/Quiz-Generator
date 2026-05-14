"""
阿里云教育 OCR 测试脚本
测试阿里云教育场景 OCR 的识别准确率和性能
"""
import sys
import os
import time
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.aliyun_ocr_service import AliyunOCRService
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_single_image(ocr_service: AliyunOCRService, image_path: str):
    """
    测试单张图片识别

    Args:
        ocr_service: OCR 服务实例
        image_path: 图片路径

    Returns:
        识别结果和耗时
    """
    print(f"\n{'=' * 60}")
    print(f"测试图片：{os.path.basename(image_path)}")
    print(f"{'=' * 60}")

    start_time = time.time()

    try:
        result = ocr_service.recognize_question_sync(image_path)
        elapsed = time.time() - start_time

        print(f"✅ 识别成功")
        print(f"⏱️  耗时：{elapsed:.2f} 秒")
        print(f"📊 置信度：{result['confidence']:.2%}")
        print(f"\n📝 识别内容：")
        print(f"   题目长度：{len(result['question'])} 字")
        print(f"   公式数量：{len(result['formulas'])} 个")
        print(f"\n   题目内容（前 200 字）：")
        print(f"   {result['question'][:200]}")

        if result['formulas']:
            print(f"\n   数学公式：")
            for i, formula in enumerate(result['formulas'][:3], 1):
                print(f"   [{i}] {formula}")

        return {
            "success": True,
            "confidence": result['confidence'],
            "elapsed": elapsed,
            "question_length": len(result['question']),
            "formula_count": len(result['formulas'])
        }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 识别失败：{str(e)}")
        print(f"⏱️  耗时：{elapsed:.2f} 秒")
        return {
            "success": False,
            "error": str(e),
            "elapsed": elapsed
        }


def main():
    """主测试流程"""
    print("=" * 60)
    print("阿里云教育 OCR 测试")
    print("=" * 60)

    # 1. 检查环境变量
    if not os.getenv("ALIYUN_ACCESS_KEY_ID"):
        print("\n❌ 错误：未设置 ALIYUN_ACCESS_KEY_ID 环境变量")
        print("\n请在 backend/.env 文件中添加：")
        print("ALIYUN_ACCESS_KEY_ID=your_access_key_id")
        print("ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret")
        return

    # 2. 初始化 OCR 服务
    try:
        ocr_service = AliyunOCRService()
        print("✅ OCR 服务初始化成功")
    except Exception as e:
        print(f"❌ OCR 服务初始化失败：{str(e)}")
        return

    # 3. 查找测试图片
    test_images_dir = backend_dir / "test_images"
    if not test_images_dir.exists():
        print(f"\n⚠️  测试图片目录不存在：{test_images_dir}")
        print("创建测试图片目录...")
        test_images_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n请将测试图片（.jpg/.png）放入目录：{test_images_dir}")
        return

    image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))

    if not image_files:
        print(f"\n⚠️  未找到测试图片")
        print(f"请将测试图片（.jpg/.png）放入目录：{test_images_dir}")
        return

    print(f"\n找到 {len(image_files)} 张测试图片")

    # 4. 测试图片识别
    results = []
    for image_path in image_files[:10]:  # 最多测试 10 张
        result = test_single_image(ocr_service, str(image_path))
        results.append(result)
        time.sleep(0.5)  # 避免 API 频率限制

    # 5. 统计结果
    print(f"\n{'=' * 60}")
    print("测试结果统计")
    print(f"{'=' * 60}")

    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    success_rate = success_count / total if total > 0 else 0

    print(f"\n📊 总体统计：")
    print(f"   测试图片数：{total} 张")
    print(f"   识别成功：{success_count} 张")
    print(f"   识别失败：{total - success_count} 张")
    print(f"   成功率：{success_rate:.2%}")

    if success_count > 0:
        successful_results = [r for r in results if r["success"]]
        avg_confidence = sum(r["confidence"] for r in successful_results) / success_count
        avg_elapsed = sum(r["elapsed"] for r in successful_results) / success_count

        print(f"\n⏱️  性能统计：")
        print(f"   平均耗时：{avg_elapsed:.2f} 秒")
        print(f"   平均置信度：{avg_confidence:.2%}")

    # 6. 验收标准检查
    print(f"\n{'=' * 60}")
    print("验收标准检查")
    print(f"{'=' * 60}")

    checks = [
        ("识别成功率", success_rate, 0.90, "≥90%"),
        ("平均置信度", avg_confidence if success_count > 0 else 0, 0.90, "≥90%"),
        ("平均耗时", avg_elapsed if success_count > 0 else 999, 3.0, "≤3秒"),
    ]

    all_pass = True
    for name, value, threshold, desc in checks:
        if name == "平均耗时":
            passed = value <= threshold
            symbol = "≤"
        else:
            passed = value >= threshold
            symbol = "≥"

        status = "✅ 通过" if passed else "❌ 未通过"
        if name in ["识别成功率", "平均置信度"]:
            print(f"   {name}：{value:.2%} {symbol} {desc} {status}")
        else:
            print(f"   {name}：{value:.2f}秒 {symbol} {desc} {status}")

        if not passed:
            all_pass = False

    print(f"\n{'=' * 60}")
    if all_pass:
        print("🎉 所有验收标准通过！")
    else:
        print("⚠️  部分验收标准未通过，请优化或调整参数")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
