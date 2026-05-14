"""
题目相关数据模型
"""

from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base
from .enums import Subject, Grade, QuestionType, Difficulty
import uuid


# 题目-知识点关联表（多对多）
QuestionKnowledgePoint = Table(
    'question_knowledge_point',
    Base.metadata,
    Column('question_id', String(36), ForeignKey('questions.id'), primary_key=True),
    Column('knowledge_point_id', Integer, ForeignKey('knowledge_points.id'), primary_key=True)
)


class Question(Base):
    """题目表"""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基础属性
    subject = Column(SQLEnum(Subject), nullable=False, index=True)
    grade = Column(SQLEnum(Grade), nullable=False, index=True)
    question_type = Column(SQLEnum(QuestionType), nullable=False, index=True)
    difficulty = Column(SQLEnum(Difficulty), nullable=False, index=True)

    # 题目内容
    content = Column(Text, nullable=False)  # 题干
    options = Column(Text, nullable=True)  # 选项（JSON 字符串，如 '["A. xxx", "B. yyy"]'）
    answer = Column(Text, nullable=False)  # 答案
    analysis = Column(Text, nullable=True)  # 解析

    # 分值（默认）
    default_score = Column(Integer, default=5)

    # 元数据
    source = Column(String(100), nullable=True)  # 来源（如"2023年中考真题"）
    chapter = Column(String(100), nullable=True)  # 章节（如"第二章 函数"）

    # 关联关系
    knowledge_points = relationship(
        "KnowledgePoint",
        secondary=QuestionKnowledgePoint,
        back_populates="questions"
    )

    def to_dict(self):
        """转为字典（用于 JSON 序列化）"""
        return {
            "id": self.id,
            "subject": self.subject.value,
            "grade": self.grade.value,
            "question_type": self.question_type.value,
            "difficulty": self.difficulty.value,
            "content": self.content,
            "options": self.options,
            "answer": self.answer,
            "analysis": self.analysis,
            "default_score": self.default_score,
            "source": self.source,
            "chapter": self.chapter,
            "knowledge_points": [kp.name for kp in self.knowledge_points]
        }


class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    subject = Column(SQLEnum(Subject), nullable=False, index=True)
    grade = Column(SQLEnum(Grade), nullable=True, index=True)

    # 层级关系（如"函数" 的父级是 "代数"）
    parent_id = Column(Integer, ForeignKey('knowledge_points.id'), nullable=True)

    # 描述
    description = Column(Text, nullable=True)

    # 关联关系
    questions = relationship(
        "Question",
        secondary=QuestionKnowledgePoint,
        back_populates="knowledge_points"
    )

    def to_dict(self):
        """转为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "subject": self.subject.value,
            "grade": self.grade.value if self.grade else None,
            "parent_id": self.parent_id,
            "description": self.description
        }
