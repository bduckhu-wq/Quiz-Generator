"""
枚举类型定义
"""

from enum import Enum


class Subject(str, Enum):
    """学科"""
    MATH = "数学"
    PHYSICS = "物理"
    CHEMISTRY = "化学"
    BIOLOGY = "生物"
    CHINESE = "语文"
    ENGLISH = "英语"
    HISTORY = "历史"
    GEOGRAPHY = "地理"
    POLITICS = "政治"


class Grade(str, Enum):
    """年级"""
    # 小学
    GRADE_1 = "一年级"
    GRADE_2 = "二年级"
    GRADE_3 = "三年级"
    GRADE_4 = "四年级"
    GRADE_5 = "五年级"
    GRADE_6 = "六年级"
    # 初中
    GRADE_7 = "初一"
    GRADE_8 = "初二"
    GRADE_9 = "初三"
    # 高中
    GRADE_10 = "高一"
    GRADE_11 = "高二"
    GRADE_12 = "高三"


class QuestionType(str, Enum):
    """题型（18种）"""
    # 选择题系列
    SINGLE_CHOICE = "单选题"
    MULTIPLE_CHOICE = "多选题"
    TRUE_FALSE = "判断题"

    # 填空题系列
    BLANK = "填空题"
    COMPLETION = "完形填空"

    # 解答题系列
    CALCULATION = "计算题"
    PROOF = "证明题"
    SOLUTION = "解答题"
    APPLICATION = "应用题"

    # 实验题系列
    EXPERIMENT = "实验题"
    EXPERIMENT_DESIGN = "实验设计题"

    # 综合题系列
    COMPREHENSIVE = "综合题"
    CASE_ANALYSIS = "案例分析题"
    MATERIAL_ANALYSIS = "材料分析题"

    # 阅读写作系列
    READING_COMPREHENSION = "阅读理解"
    CLOZE = "完型填空"
    ESSAY = "作文题"
    TRANSLATION = "翻译题"


class Difficulty(str, Enum):
    """难度"""
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"
