"""
题目质量校验
"""

from typing import Dict, List, Optional
import re


class QuestionValidator:
    """题目质量校验器"""

    @staticmethod
    def validate_question(question: Dict) -> tuple[bool, Optional[str]]:
        """
        校验单个题目是否合法

        Args:
            question: 题目字典

        Returns:
            (是否合法, 错误信息)
        """
        # 必需字段
        required_fields = ["question_type", "content", "answer"]

        for field in required_fields:
            if field not in question or not question[field]:
                return False, f"缺少必需字段: {field}"

        # 题目内容长度校验
        content = question["content"]
        if len(content) < 5:
            return False, "题目内容过短"

        if len(content) > 500:
            return False, "题目内容过长"

        # 答案不能为空
        answer = question["answer"]
        if not answer or answer.strip() == "":
            return False, "答案为空"

        # 选择题必须有选项
        if "choice" in question["question_type"].lower():
            if "options" not in question or not question["options"]:
                return False, "选择题缺少选项"

            # 至少 2 个选项
            if len(question["options"]) < 2:
                return False, "选择题选项不足"

        return True, None

    @staticmethod
    def validate_batch(questions: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """
        批量校验题目

        Args:
            questions: 题目列表

        Returns:
            (合法题目列表, 不合法题目列表)
        """
        valid_questions = []
        invalid_questions = []

        for idx, question in enumerate(questions):
            is_valid, error = QuestionValidator.validate_question(question)

            if is_valid:
                valid_questions.append(question)
            else:
                invalid_questions.append({
                    "index": idx,
                    "question": question,
                    "error": error
                })

        return valid_questions, invalid_questions

    @staticmethod
    def extract_reference_style(reference_questions: List[Dict]) -> Dict:
        """
        从参考题目中提取风格特征

        Args:
            reference_questions: 参考题目列表

        Returns:
            风格特征字典
        """
        if not reference_questions:
            return {}

        # 统计特征
        avg_content_length = sum(len(q.get("content", "")) for q in reference_questions) / len(reference_questions)

        # 答案风格（简洁 vs 详细）
        avg_answer_length = sum(len(q.get("answer", "")) for q in reference_questions) / len(reference_questions)

        # 是否包含解析
        has_analysis_rate = sum(1 for q in reference_questions if q.get("analysis")) / len(reference_questions)

        return {
            "avg_content_length": int(avg_content_length),
            "avg_answer_length": int(avg_answer_length),
            "has_analysis_rate": has_analysis_rate,
            "typical_content_length_range": f"{int(avg_content_length * 0.7)}-{int(avg_content_length * 1.3)}"
        }

    @staticmethod
    def format_fix_suggestions(question: Dict) -> str:
        """
        生成题目修复建议

        Args:
            question: 有问题的题目

        Returns:
            修复建议文本
        """
        is_valid, error = QuestionValidator.validate_question(question)

        if is_valid:
            return "题目格式正确"

        suggestions = [f"问题: {error}"]

        # 根据错误类型给出建议
        if "缺少必需字段" in error:
            suggestions.append("建议: 补充缺失字段")

        if "题目内容过短" in error:
            suggestions.append("建议: 补充题目描述，使其更清晰")

        if "答案为空" in error:
            suggestions.append("建议: 提供正确答案")

        if "选择题缺少选项" in error:
            suggestions.append("建议: 添加至少 4 个选项（A/B/C/D）")

        return "\n".join(suggestions)
