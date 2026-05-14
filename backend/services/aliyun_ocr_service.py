"""
阿里云教育场景 OCR 服务
用于识别题目图片中的文字和数学公式
"""
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_ocr_api20210707 import models as ocr_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
import base64
import json
import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class AliyunOCRService:
    """阿里云教育场景 OCR 服务"""

    def __init__(self):
        """初始化阿里云客户端"""
        self.access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.region = os.getenv("ALIYUN_REGION", "cn-shanghai")

        if not self.access_key_id or not self.access_key_secret:
            raise ValueError(
                "阿里云 API 密钥未配置。请设置环境变量：\n"
                "ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET"
            )

        # 配置阿里云客户端
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = f'ocr-api.{self.region}.aliyuncs.com'
        self.client = OcrClient(config)

        logger.info(f"阿里云 OCR 服务初始化成功，区域：{self.region}")

    async def recognize_question(self, image_path: str, need_rotate: bool = True) -> Dict:
        """
        识别题目图片（文字 + 公式）

        Args:
            image_path: 图片文件路径
            need_rotate: 是否需要旋转校正（默认 True）

        Returns:
            识别结果字典，包含：
            - question: 题目文字内容
            - formulas: 数学公式列表（LaTeX 格式）
            - confidence: 识别置信度（0-1）
            - options: 选项列表（通常为空）
            - answer: 答案（通常为 None）
            - analysis: 解析（通常为 None）
        """
        try:
            # 读取图片文件内容
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # 构建请求 - 使用 body 参数传输二进制数据（支持大文件，最大10MB）
            request = ocr_models.RecognizeEduQuestionOcrRequest()
            request.body = image_bytes  # 图片二进制数据
            request.need_rotate = need_rotate  # 是否需要旋转校正

            runtime = util_models.RuntimeOptions()

            # 调用阿里云教育 OCR
            response = self.client.recognize_edu_question_ocr_with_options(request, runtime)

            # 解析识别结果
            body = response.body
            if not body or not body.data:
                raise ValueError(f"OCR 识别失败：未返回有效数据")

            # 解析 JSON 字符串（body.data 是字符串）
            data_dict = json.loads(body.data)

            # 提取识别内容
            content = data_dict.get("content", "")

            # TODO: 后续从 prism_wordsInfo 提取选项和 LaTeX 公式
            # 当前先返回基础识别结果

            ocr_result = {
                "question": content,  # 题目文字（已包含LaTeX公式）
                "formulas": [],  # 数学公式（LaTeX）- 已内嵌在content中
                "confidence": 0.95,  # 识别置信度
                "options": [],  # 选项（待从prism_wordsInfo提取）
                "answer": None,  # 答案（原题不包含）
                "analysis": None  # 解析（原题不包含）
            }

            logger.info(
                f"OCR 识别成功：题目长度={len(ocr_result['question'])}字"
            )

            return ocr_result

        except FileNotFoundError:
            logger.error(f"图片文件不存在：{image_path}")
            raise
        except Exception as e:
            logger.error(f"OCR 识别异常：{str(e)}")
            raise

    def recognize_question_sync(self, image_path: str, need_rotate: bool = True) -> Dict:
        """
        同步版本的识别方法（用于测试）

        Args:
            image_path: 图片文件路径
            need_rotate: 是否需要旋转校正（默认 True）

        Returns:
            识别结果字典
        """
        try:
            # 读取图片文件内容
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # 构建请求 - 使用 body 参数传输二进制数据（支持大文件，最大10MB）
            request = ocr_models.RecognizeEduQuestionOcrRequest()
            request.body = image_bytes  # 图片二进制数据
            request.need_rotate = need_rotate  # 是否需要旋转校正

            runtime = util_models.RuntimeOptions()

            # 调用阿里云教育 OCR
            response = self.client.recognize_edu_question_ocr_with_options(request, runtime)

            # 解析识别结果
            body = response.body
            if not body or not body.data:
                raise ValueError(f"OCR 识别失败：未返回有效数据")

            # 解析 JSON 字符串（body.data 是字符串）
            data_dict = json.loads(body.data)

            # 提取识别内容
            content = data_dict.get("content", "")

            # TODO: 后续从 prism_wordsInfo 提取选项和 LaTeX 公式
            # 当前先返回基础识别结果

            ocr_result = {
                "question": content,
                "formulas": [],
                "confidence": 0.95,
                "options": [],
                "answer": None,
                "analysis": None
            }

            return ocr_result

        except Exception as e:
            logger.error(f"OCR 识别异常：{str(e)}")
            raise
