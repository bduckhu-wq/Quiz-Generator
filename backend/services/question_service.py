"""
题目服务 - 数据库 CRUD 操作
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Question, KnowledgePoint, Subject, Grade, QuestionType, Difficulty


class QuestionService:
    """
    题目服务

    功能：
    1. 基础 CRUD（创建、读取、更新、删除）
    2. 条件搜索（学科、年级、知识点、难度、题型）
    3. 批量操作
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: str) -> Optional[Question]:
        """根据 ID 获取题目"""
        return self.db.query(Question).filter(Question.id == question_id).first()

    def search(
        self,
        subject: Optional[Subject] = None,
        grade: Optional[Grade] = None,
        question_types: Optional[List[QuestionType]] = None,
        difficulties: Optional[List[Difficulty]] = None,
        knowledge_points: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Question]:
        """
        条件搜索题目

        Args:
            subject: 学科
            grade: 年级
            question_types: 题型列表
            difficulties: 难度列表
            knowledge_points: 知识点列表
            limit: 返回数量
            offset: 偏移量

        Returns:
            题目列表
        """
        query = self.db.query(Question)

        # 构建过滤条件
        filters = []

        if subject:
            filters.append(Question.subject == subject)

        if grade:
            filters.append(Question.grade == grade)

        if question_types:
            filters.append(Question.question_type.in_(question_types))

        if difficulties:
            filters.append(Question.difficulty.in_(difficulties))

        if knowledge_points:
            # 构建知识点+章节过滤条件
            kp_filters = []

            for kp in knowledge_points:
                # 1. 匹配章节字段（如"第三章第二节"）
                kp_filters.append(Question.chapter == kp)
                kp_filters.append(Question.chapter.like(f"%{kp}%"))

                # 2. 匹配知识点（关联表查询）
                # 需要子查询来避免join影响结果
                kp_subquery = self.db.query(Question.id).join(Question.knowledge_points).filter(
                    or_(
                        KnowledgePoint.name == kp,
                        KnowledgePoint.name.like(f"%{kp}%")
                    )
                ).subquery()
                kp_filters.append(Question.id.in_(kp_subquery))

            filters.append(or_(*kp_filters))

        # 应用过滤
        if filters:
            query = query.filter(and_(*filters))

        # 分页
        query = query.offset(offset).limit(limit)

        return query.all()

    def get_by_knowledge_points(
        self,
        knowledge_points: List[str],
        limit: int = 20
    ) -> List[Question]:
        """
        根据知识点检索题目

        Args:
            knowledge_points: 知识点名称列表
            limit: 返回数量

        Returns:
            题目列表
        """
        return self.db.query(Question).join(Question.knowledge_points).filter(
            KnowledgePoint.name.in_(knowledge_points)
        ).limit(limit).all()

    def count(
        self,
        subject: Optional[Subject] = None,
        grade: Optional[Grade] = None,
        question_types: Optional[List[QuestionType]] = None,
        difficulties: Optional[List[Difficulty]] = None
    ) -> int:
        """
        统计满足条件的题目数量

        Args:
            subject: 学科
            grade: 年级
            question_types: 题型列表
            difficulties: 难度列表

        Returns:
            题目数量
        """
        query = self.db.query(Question)

        filters = []

        if subject:
            filters.append(Question.subject == subject)

        if grade:
            filters.append(Question.grade == grade)

        if question_types:
            filters.append(Question.question_type.in_(question_types))

        if difficulties:
            filters.append(Question.difficulty.in_(difficulties))

        if filters:
            query = query.filter(and_(*filters))

        return query.count()

    def create(self, question_data: Dict) -> Question:
        """
        创建题目

        Args:
            question_data: 题目数据字典

        Returns:
            创建的题目对象
        """
        question = Question(**question_data)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question_id: str, update_data: Dict) -> Optional[Question]:
        """
        更新题目

        Args:
            question_id: 题目 ID
            update_data: 更新数据

        Returns:
            更新后的题目对象
        """
        question = self.get_by_id(question_id)
        if not question:
            return None

        for key, value in update_data.items():
            if hasattr(question, key):
                setattr(question, key, value)

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question_id: str) -> bool:
        """
        删除题目

        Args:
            question_id: 题目 ID

        Returns:
            是否删除成功
        """
        question = self.get_by_id(question_id)
        if not question:
            return False

        self.db.delete(question)
        self.db.commit()
        return True


class KnowledgePointService:
    """知识点服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_subject(self, subject: Subject, grade: Optional[Grade] = None) -> List[KnowledgePoint]:
        """
        获取指定学科的知识点

        Args:
            subject: 学科
            grade: 年级（可选）

        Returns:
            知识点列表
        """
        query = self.db.query(KnowledgePoint).filter(KnowledgePoint.subject == subject)

        if grade:
            query = query.filter(KnowledgePoint.grade == grade)

        return query.all()

    def search_by_name(self, name: str) -> List[KnowledgePoint]:
        """
        根据名称模糊搜索知识点

        Args:
            name: 知识点名称（支持部分匹配）

        Returns:
            知识点列表
        """
        return self.db.query(KnowledgePoint).filter(
            KnowledgePoint.name.like(f"%{name}%")
        ).all()

    def get_by_id(self, kp_id: int) -> Optional[KnowledgePoint]:
        """根据 ID 获取知识点"""
        return self.db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()

    def create(self, kp_data: Dict) -> KnowledgePoint:
        """创建知识点"""
        kp = KnowledgePoint(**kp_data)
        self.db.add(kp)
        self.db.commit()
        self.db.refresh(kp)
        return kp
