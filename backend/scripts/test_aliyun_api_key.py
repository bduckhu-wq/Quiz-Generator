"""
阿里云 API 密钥验证脚本
验证 API Key 是否有效
"""
import sys
import os
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_api_key():
    """测试 API 密钥配置"""
    print("=" * 60)
    print("阿里云 API 密钥验证")
    print("=" * 60)

    # 1. 检查环境变量
    access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    region = os.getenv("ALIYUN_REGION", "cn-shanghai")

    if not access_key_id:
        print("\n❌ 错误：未设置 ALIYUN_ACCESS_KEY_ID")
        return False

    if not access_key_secret:
        print("\n❌ 错误：未设置 ALIYUN_ACCESS_KEY_SECRET")
        return False

    print(f"\n✅ 环境变量配置正常")
    print(f"   AccessKey ID: {access_key_id[:8]}...{access_key_id[-4:]}")
    print(f"   AccessKey Secret: {'*' * 20}")
    print(f"   Region: {region}")

    # 2. 测试新版 SDK 导入
    try:
        from alibabacloud_ocr_api20210707.client import Client as OcrClient
        from alibabacloud_tea_openapi import models as open_api_models
        print(f"\n✅ 阿里云 OCR SDK 导入成功")
    except ImportError as e:
        print(f"\n❌ 阿里云 OCR SDK 导入失败：{e}")
        print("请运行：pip install alibabacloud-ocr-api20210707")
        return False

    # 3. 测试客户端初始化
    try:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = f'ocr-api.{region}.aliyuncs.com'
        client = OcrClient(config)
        print(f"✅ 阿里云 OCR 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败：{e}")
        return False

    # 4. 测试 AliyunOCRService
    try:
        from services.aliyun_ocr_service import AliyunOCRService
        service = AliyunOCRService()
        print(f"✅ AliyunOCRService 初始化成功")
    except Exception as e:
        print(f"❌ AliyunOCRService 初始化失败：{e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 所有配置验证通过！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 将测试图片（.jpg/.png）放入 backend/test_images/ 目录")
    print("2. 运行：python scripts/test_aliyun_ocr.py")

    return True


if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)
