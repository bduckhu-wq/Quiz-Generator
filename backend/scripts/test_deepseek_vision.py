"""
DeepSeek V4 Vision API 测试脚本

功能：
1. 测试 DeepSeek V4 Vision API 的 OCR 识别能力
2. 测试参数推断准确率（学科/年级/知识点/题型/难度）
3. 记录识别准确率，为正式开发提供数据支撑

使用方法：
python backend/scripts/test_deepseek_vision.py
"""

import os
import sys
import base64
import json
import asyncio
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DeepSeekVisionTester:
    """DeepSeek V4 Vision API 测试器"""

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("❌ 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        print(f"✅ DeepSeek API 初始化成功")
        print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")

    def _build_ocr_prompt(self) -> str:
        """构建 OCR 识别 Prompt"""
        return """请识别图片中的题目内容，并推断学科、年级、知识点等参数。直接输出 JSON 格式（不要有任何其他文字）：

{"question":"题目内容","options":["A.xxx","B.xxx"],"answer":null,"subject":"数学","grade":"初二","knowledge_point":"知识点","question_type":"选择题","difficulty":"中等","confidence":0.95}

字段说明：
- question: 完整题目文字（必填）
- options: 选项数组，图片中有选项才填，否则为空数组 []
- answer: 答案，图片中有才填，否则为 null
- subject: 学科（数学/物理/化学/语文/英语等）
- grade: 年级（初一/初二/初三/高一/高二/高三等）
- knowledge_point: 具体知识点名称
- question_type: 题型（选择题/填空题/应用题/解答题等）
- difficulty: 难度（简单/中等/困难）
- confidence: 识别置信度 0-1

现在请识别下面这张图片："""

    async def recognize_image(self, image_path: str) -> dict:
        """
        识别单张图片

        Args:
            image_path: 图片路径

        Returns:
            识别结果 JSON
        """
        # 读取图片为 base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # 调用 DeepSeek V4 多模态 API
        # DeepSeek 支持在纯文本中嵌入 base64 图片
        try:
            prompt_with_image = f"{self._build_ocr_prompt()}data:image/png;base64,{image_data}"

            response = await self.client.chat.completions.create(
                model="deepseek-chat",  # DeepSeek V4 多模态模型
                messages=[
                    {
                        "role": "user",
                        "content": prompt_with_image
                    }
                ],
                temperature=0.0  # 确定性输出
            )

            # 获取响应内容
            content = response.choices[0].message.content

            # 尝试解析 JSON（如果包含 JSON 代码块，先提取）
            if "```json" in content:
                # 提取 JSON 代码块
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "{" in content and "}" in content:
                # 直接提取 JSON 部分
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
            else:
                # 整个内容作为 JSON
                json_str = content

            # 解析 JSON
            result = json.loads(json_str)

            # 添加元数据
            result["image_path"] = image_path
            result["status"] = "success"
            result["raw_response"] = content  # 保存原始响应

            return result

        except Exception as e:
            return {
                "image_path": image_path,
                "status": "error",
                "error": str(e)
            }

    async def batch_test(self, image_dir: str, limit: int = 10):
        """
        批量测试图片识别

        Args:
            image_dir: 图片目录路径
            limit: 测试图片数量限制
        """
        # 查找图片文件
        image_dir = Path(image_dir)
        if not image_dir.exists():
            print(f"❌ 图片目录不存在: {image_dir}")
            return

        image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
        image_files = image_files[:limit]

        if not image_files:
            print(f"❌ 未找到图片文件（*.jpg, *.png）: {image_dir}")
            return

        print(f"\n📁 找到 {len(image_files)} 张图片，开始测试...")
        print("=" * 80)

        results = []

        for i, image_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 正在识别: {image_file.name}")

            result = await self.recognize_image(str(image_file))
            results.append(result)

            if result["status"] == "success":
                print(f"✅ 识别成功")
                print(f"   题目: {result['question'][:50]}...")
                print(f"   学科: {result.get('subject', 'N/A')}")
                print(f"   年级: {result.get('grade', 'N/A')}")
                print(f"   知识点: {result.get('knowledge_point', 'N/A')}")
                print(f"   题型: {result.get('question_type', 'N/A')}")
                print(f"   难度: {result.get('difficulty', 'N/A')}")
                print(f"   置信度: {result.get('confidence', 0):.2f}")
            else:
                print(f"❌ 识别失败: {result['error']}")

        # 统计结果
        print("\n" + "=" * 80)
        print("📊 测试统计")
        print("=" * 80)

        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        success_rate = success_count / len(results) * 100 if results else 0

        print(f"总测试数: {len(results)}")
        print(f"成功识别: {success_count} ({success_rate:.1f}%)")
        print(f"识别失败: {error_count}")

        if success_count > 0:
            avg_confidence = sum(r.get("confidence", 0) for r in results if r["status"] == "success") / success_count
            print(f"平均置信度: {avg_confidence:.2f}")

        # 保存结果
        output_file = Path("backend/scripts/deepseek_vision_test_results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 测试结果已保存到: {output_file}")

        return results

    async def single_test(self, image_path: str):
        """
        单图测试（用于快速验证）

        Args:
            image_path: 图片路径
        """
        print(f"🔍 正在识别: {image_path}")
        print("=" * 80)

        result = await self.recognize_image(image_path)

        if result["status"] == "success":
            print(f"✅ 识别成功\n")
            print(f"题目内容:\n{result['question']}\n")
            print(f"学科: {result.get('subject', 'N/A')}")
            print(f"年级: {result.get('grade', 'N/A')}")
            print(f"知识点: {result.get('knowledge_point', 'N/A')}")
            print(f"题型: {result.get('question_type', 'N/A')}")
            print(f"难度: {result.get('difficulty', 'N/A')}")
            print(f"置信度: {result.get('confidence', 0):.2f}")

            if result.get('options'):
                print(f"\n选项:")
                for opt in result['options']:
                    print(f"  {opt}")

            if result.get('answer'):
                print(f"\n答案: {result['answer']}")
        else:
            print(f"❌ 识别失败: {result['error']}")

        return result


async def main():
    """主函数"""
    tester = DeepSeekVisionTester()

    # 模式选择
    print("\n" + "=" * 80)
    print("DeepSeek V4 Vision API 测试工具")
    print("=" * 80)
    print("\n选择测试模式:")
    print("1. 单图测试（快速验证）")
    print("2. 批量测试（测试目录下所有图片）")

    mode = input("\n请输入模式（1 或 2）: ").strip()

    if mode == "1":
        # 单图测试
        image_path = input("请输入图片路径: ").strip()
        if not os.path.exists(image_path):
            print(f"❌ 图片不存在: {image_path}")
            return

        await tester.single_test(image_path)

    elif mode == "2":
        # 批量测试
        image_dir = input("请输入图片目录路径（留空使用默认 test_images/）: ").strip()
        if not image_dir:
            image_dir = "test_images"

        limit = input("测试图片数量限制（留空默认 10 张）: ").strip()
        limit = int(limit) if limit.isdigit() else 10

        await tester.batch_test(image_dir, limit)

    else:
        print("❌ 无效的模式选择")


if __name__ == "__main__":
    asyncio.run(main())
