"""
补充小学三年级数学题目
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import SessionLocal
from models.question import Question, KnowledgePoint
from models.enums import Subject, Grade, QuestionType, Difficulty
import uuid


def add_grade3_questions():
    """添加小学三年级数学题目"""
    db = SessionLocal()

    try:
        # 1. 创建知识点
        kp1 = KnowledgePoint(
            name="第三章第二节",
            subject=Subject.MATH,
            grade=Grade.GRADE_3,
            description="小学三年级数学下学期第三章第二节"
        )
        db.add(kp1)
        db.flush()

        # 2. 创建题目
        import json

        questions = [
            # 单选题
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "25 + 38 = ?",
                "options": json.dumps(["A. 53", "B. 63", "C. 73", "D. 83"]),
                "answer": "B",
                "analysis": "25 + 38 = 63，注意进位",
                "default_score": 5,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "72 - 29 = ?",
                "options": json.dumps(["A. 43", "B. 44", "C. 53", "D. 54"]),
                "answer": "A",
                "analysis": "72 - 29 = 43，借位计算",
                "default_score": 5,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            # 填空题
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "56 + ____ = 100",
                "options": None,
                "answer": "44",
                "analysis": "100 - 56 = 44",
                "default_score": 6,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "一个数加上27等于85，这个数是____。",
                "options": None,
                "answer": "58",
                "analysis": "85 - 27 = 58",
                "default_score": 6,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            # 计算题
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "竖式计算：\n(1) 345 + 289\n(2) 602 - 347",
                "options": None,
                "answer": "(1) 634\n(2) 255",
                "analysis": "(1) 345 + 289 = 634\n(2) 602 - 347 = 255",
                "default_score": 8,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            # 应用题
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "小明有45块糖，小红有38块糖。他们一共有多少块糖？",
                "options": None,
                "answer": "83块",
                "analysis": "45 + 38 = 83（块）",
                "default_score": 10,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "水果店原有96个苹果，卖出了58个，还剩多少个？",
                "options": None,
                "answer": "38个",
                "analysis": "96 - 58 = 38（个）",
                "default_score": 10,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            # 额外补充题目
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "123 + 456 = ?",
                "options": json.dumps(["A. 579", "B. 589", "C. 599", "D. 609"]),
                "answer": "A",
                "analysis": "123 + 456 = 579",
                "default_score": 5,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "300 - 165 = ____",
                "options": None,
                "answer": "135",
                "analysis": "300 - 165 = 135",
                "default_score": 5,
                "source": "课后练习",
                "chapter": "第三章第二节"
            },
            {
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "学校图书馆有故事书235本，科技书168本。故事书比科技书多多少本？",
                "options": None,
                "answer": "67本",
                "analysis": "235 - 168 = 67（本）",
                "default_score": 8,
                "source": "课后练习",
                "chapter": "第三章第二节"
            }
        ]

        for q_data in questions:
            q = Question(
                id=str(uuid.uuid4()),
                **q_data
            )
            db.add(q)
            db.flush()

            # 关联知识点
            q.knowledge_points.append(kp1)

        db.commit()
        print(f"✓ 成功添加 {len(questions)} 道三年级数学题目")
        print(f"✓ 知识点: {kp1.name}")

    except Exception as e:
        db.rollback()
        print(f"❌ 添加失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    add_grade3_questions()
