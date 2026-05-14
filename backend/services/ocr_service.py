"""
OCR 识别服务

负责识别试题图片，提取题目内容、公式、选项等结构化信息
"""

import os
import base64
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """OCR 识别结果"""
    question: str  # 题目内容
    formulas: list[str]  # LaTeX 格式公式
    options: list[str]  # 选项（如 ["A. xxx", "B. yyy"]）
    answer: Optional[str]  # 答案
    analysis: Optional[str]  # 解析
    subject: Optional[str]  # 学科（AI 推断）
    grade: Optional[str]  # 年级（AI 推断）
    knowledge_point: Optional[str]  # 知识点（AI 推断）
    question_type: Optional[str]  # 题型（choice/blank/solution/judge）
    difficulty: Optional[str]  # 难度（easy/medium/hard）
    confidence: float  # OCR 识别置信度


class OCRService:
    """OCR 服务 - 阿里云教育场景 OCR"""

    def __init__(self):
        """初始化阿里云 OCR 客户端"""
        self.client = self._init_aliyun_client()

    def _init_aliyun_client(self):
        """初始化阿里云客户端"""
        try:
            from alibabacloud_ocr_api20210707.client import Client
            from alibabacloud_tea_openapi.models import Config

            access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
            access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")

            if not access_key_id or not access_key_secret:
                raise ValueError(
                    "阿里云 OCR 配置缺失：请设置环境变量 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET"
                )

            config = Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret
            )

            client = Client(config)
            logger.info("阿里云 OCR 客户端初始化成功")
            return client

        except ImportError:
            raise ImportError(
                "阿里云 OCR SDK 未安装，请执行：pip install alibabacloud-ocr-api20210707"
            )
        except Exception as e:
            logger.error(f"阿里云 OCR 客户端初始化失败：{e}")
            raise

    async def recognize_question(
        self,
        image_path: str,
        image_url: Optional[str] = None
    ) -> OCRResult:
        """
        识别试题图片

        Args:
            image_path: 本地图片路径（优先）
            image_url: 图片 URL（当 image_path 为空时使用）

        Returns:
            OCRResult: 识别结果

        Raises:
            ValueError: 参数错误
            Exception: OCR 识别失败
        """
        if not image_path and not image_url:
            raise ValueError("image_path 和 image_url 至少提供一个")

        try:
            # 构建请求参数
            request_body = {}

            if image_path:
                # 读取本地图片并转 Base64
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                request_body["body"] = image_data
                logger.info(f"识别本地图片：{image_path}")
            else:
                # 使用图片 URL
                request_body["url"] = image_url
                logger.info(f"识别远程图片：{image_url}")

            # 调用阿里云教育场景 OCR API
            response = self.client.recognize_edu_question_ocr(request_body)

            # 解析响应
            data = response.body.data

            # 构建返回结果
            result = OCRResult(
                question=data.content or "",
                formulas=self._extract_formulas(data),
                options=self._extract_options(data),
                answer=getattr(data, "answer", None),
                analysis=getattr(data, "analysis", None),
                subject=self._infer_subject(data),
                grade=self._infer_grade(data),
                knowledge_point=getattr(data, "knowledge_point", None),
                question_type=self._infer_question_type(data),
                difficulty=self._infer_difficulty(data),
                confidence=getattr(data, "confidence", 0.95)
            )

            logger.info(
                f"OCR 识别成功，置信度：{result.confidence:.2f}，"
                f"题目长度：{len(result.question)} 字符"
            )

            return result

        except FileNotFoundError:
            error_msg = f"图片文件不存在：{image_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        except Exception as e:
            error_msg = f"OCR 识别失败：{str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _extract_formulas(self, data) -> list[str]:
        """提取 LaTeX 公式"""
        formulas = []

        # 方法1：从 latex_formulas 字段提取
        if hasattr(data, "latex_formulas") and data.latex_formulas:
            formulas.extend(data.latex_formulas)

        # 方法2：从 content 中提取（查找 $...$ 或 $$...$$）
        if hasattr(data, "content") and data.content:
            import re
            # 匹配 $...$ 或 $$...$$ 格式的公式
            pattern = r'\$\$?(.*?)\$\$?'
            matches = re.findall(pattern, data.content)
            formulas.extend(matches)

        return list(set(formulas))  # 去重

    def _extract_options(self, data) -> list[str]:
        """提取选项"""
        options = []

        # 方法1：从 options 字段提取
        if hasattr(data, "options") and data.options:
            options = data.options

        # 方法2：从 content 中提取（识别 A. B. C. D. 格式）
        elif hasattr(data, "content") and data.content:
            import re
            # 匹配 A. xxx\nB. yyy\n 格式
            pattern = r'([A-D]\.)\s*([^\n]+)'
            matches = re.findall(pattern, data.content)
            options = [f"{label} {text}" for label, text in matches]

        return options

    def _infer_subject(self, data) -> Optional[str]:
        """推断学科"""
        if hasattr(data, "subject") and data.subject:
            return data.subject

        # 简单规则推断（可后续用 LLM 增强）
        content = getattr(data, "content", "")

        if any(keyword in content for keyword in ["方程", "函数", "几何", "三角形", "圆"]):
            return "数学"
        elif any(keyword in content for keyword in ["力", "速度", "电流", "电压"]):
            return "物理"
        elif any(keyword in content for keyword in ["化学式", "反应", "元素", "氧化"]):
            return "化学"

        return None

    def _infer_grade(self, data) -> Optional[str]:
        """推断年级"""
        if hasattr(data, "grade") and data.grade:
            return data.grade

        # TODO: 可根据知识点难度推断年级
        return None

    def _infer_question_type(self, data) -> Optional[str]:
        """推断题型"""
        # 有选项 → 选择题
        if self._extract_options(data):
            return "choice"

        content = getattr(data, "content", "")

        # 判断题
        if "判断" in content or "对错" in content or "正确的是" in content:
            return "judge"

        # 填空题
        if "填空" in content or "____" in content or "（  ）" in content:
            return "blank"

        # 解答题
        if "计算" in content or "证明" in content or "求" in content:
            return "solution"

        return None

    def _infer_difficulty(self, data) -> Optional[str]:
        """推断难度"""
        if hasattr(data, "difficulty") and data.difficulty:
            # 归一化难度值
            difficulty_map = {
                "简单": "easy",
                "容易": "easy",
                "中等": "medium",
                "适中": "medium",
                "困难": "hard",
                "较难": "hard"
            }
            return difficulty_map.get(data.difficulty, "medium")

        return "medium"  # 默认中等难度


# 全局单例
_ocr_service_instance = None


def get_ocr_service() -> OCRService:
    """获取 OCR 服务单例"""
    global _ocr_service_instance
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService()
    return _ocr_service_instance
