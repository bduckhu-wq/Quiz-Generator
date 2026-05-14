"""
测试题目服务（CRUD 操作）

用法：
python scripts/test_question_service.py
"""

import sys
import os

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import SessionLocal
from models import Subject, Grade, QuestionType, Difficulty
from services.question_service import QuestionService, KnowledgePointService


def test_question_service():
    """测试题目服务"""

    print("\n" + "="*60)
    print("测试题目服务（CRUD 操作）")
    print("="*60 + "\n")

    db = SessionLocal()
    question_service = QuestionService(db)
    kp_service = KnowledgePointService(db)

    try:
        # 测试 1: 查询知识点
        print("测试 1: 查询知识点")
        print("-" * 60)
        math_kps = kp_service.get_by_subject(Subject.MATH, Grade.GRADE_8)
        print(f"✓ 初二数学知识点: {len(math_kps)} 个")
        print(f"  示例: {', '.join([kp.name for kp in math_kps[:5]])}\n")

        # 测试 2: 按学科+年级搜索题目
        print("测试 2: 按学科+年级搜索题目")
        print("-" * 60)
        questions = question_service.search(
            subject=Subject.MATH,
            grade=Grade.GRADE_8,
            limit=5
        )
        print(f"✓ 初二数学题目: {len(questions)} 道（取前5）")
        for q in questions:
            print(f"  • [{q.question_type.value}] {q.content[:50]}...")
        print()

        # 测试 3: 按难度搜索
        print("测试 3: 按难度搜索题目")
        print("-" * 60)
        hard_questions = question_service.search(
            subject=Subject.PHYSICS,
            difficulties=[Difficulty.HARD],
            limit=5
        )
        print(f"✓ 物理困难题: {len(hard_questions)} 道")
        for q in hard_questions:
            print(f"  • [{q.difficulty.value}] {q.content[:50]}...")
        print()

        # 测试 4: 按题型搜索
        print("测试 4: 按题型搜索题目")
        print("-" * 60)
        choice_questions = question_service.search(
            subject=Subject.MATH,
            question_types=[QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE],
            limit=5
        )
        print(f"✓ 数学选择题: {len(choice_questions)} 道")
        for q in choice_questions:
            print(f"  • [{q.question_type.value}] {q.content[:50]}...")
        print()

        # 测试 5: 按知识点搜索
        print("测试 5: 按知识点搜索题目")
        print("-" * 60)
        kp_questions = question_service.get_by_knowledge_points(
            knowledge_points=["一元一次方程", "二次函数"],
            limit=5
        )
        print(f"✓ 包含指定知识点的题目: {len(kp_questions)} 道")
        for q in kp_questions:
            kp_names = [kp.name for kp in q.knowledge_points]
            print(f"  • {q.content[:40]}... (知识点: {', '.join(kp_names)})")
        print()

        # 测试 6: 统计题目数量
        print("测试 6: 统计题目数量")
        print("-" * 60)
        total_math = question_service.count(subject=Subject.MATH)
        total_physics = question_service.count(subject=Subject.PHYSICS)
        print(f"✓ 数学题目总数: {total_math} 道")
        print(f"✓ 物理题目总数: {total_physics} 道")
        print()

        # 测试 7: 按难度统计
        print("测试 7: 按难度统计题目数量")
        print("-" * 60)
        for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            count = question_service.count(
                subject=Subject.MATH,
                difficulties=[difficulty]
            )
            print(f"  • {difficulty.value}: {count} 道")
        print()

        # 测试 8: 获取单个题目详情
        print("测试 8: 获取题目详情")
        print("-" * 60)
        sample_question = questions[0] if questions else None
        if sample_question:
            print(f"✓ 题目 ID: {sample_question.id}")
            print(f"  学科: {sample_question.subject.value}")
            print(f"  年级: {sample_question.grade.value}")
            print(f"  题型: {sample_question.question_type.value}")
            print(f"  难度: {sample_question.difficulty.value}")
            print(f"  内容: {sample_question.content}")
            print(f"  答案: {sample_question.answer}")
            print(f"  解析: {sample_question.analysis}")
            print(f"  知识点: {', '.join([kp.name for kp in sample_question.knowledge_points])}")
        print()

        # 总结
        print("="*60)
        print("✅ 题目服务所有测试通过！")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_question_service()
    sys.exit(0 if success else 1)
