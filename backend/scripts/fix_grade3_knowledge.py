"""
修正三年级数据：区分章节和知识点
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import SessionLocal
from models.question import Question, KnowledgePoint
from models.enums import Subject, Grade


def fix_knowledge_points():
    """修正知识点数据"""
    db = SessionLocal()

    try:
        # 1. 删除错误的知识点（章节名不是知识点）
        wrong_kp = db.query(KnowledgePoint).filter(
            KnowledgePoint.name == "第三章第二节"
        ).first()

        if wrong_kp:
            db.delete(wrong_kp)
            print("✓ 删除错误知识点: 第三章第二节")

        # 2. 创建正确的知识点
        knowledge_points = [
            {
                "name": "两位数加减法",
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "description": "三年级两位数、三位数的加减运算"
            },
            {
                "name": "进位加法",
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "description": "带进位的加法运算"
            },
            {
                "name": "退位减法",
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "description": "带退位（借位）的减法运算"
            },
            {
                "name": "加减法应用",
                "subject": Subject.MATH,
                "grade": Grade.GRADE_3,
                "description": "加减法在实际问题中的应用"
            }
        ]

        kp_map = {}
        for kp_data in knowledge_points:
            kp = KnowledgePoint(**kp_data)
            db.add(kp)
            db.flush()
            kp_map[kp.name] = kp
            print(f"✓ 创建知识点: {kp.name}")

        # 3. 重新关联题目
        questions = db.query(Question).filter(Question.grade == Grade.GRADE_3).all()

        for q in questions:
            # 清空旧关联
            q.knowledge_points.clear()

            # 根据题目内容分配知识点
            content = q.content

            # 判断知识点
            if "+" in content and any(word in content for word in ["小明", "小红", "苹果", "糖"]):
                # 应用题
                q.knowledge_points.append(kp_map["加减法应用"])
                q.knowledge_points.append(kp_map["两位数加减法"])
            elif "+" in content:
                # 加法题
                q.knowledge_points.append(kp_map["两位数加减法"])
                if any(c in content for c in ["进位", "38", "89", "456"]):  # 可能有进位
                    q.knowledge_points.append(kp_map["进位加法"])
            elif "-" in content or "剩" in content:
                # 减法题
                q.knowledge_points.append(kp_map["两位数加减法"])
                if any(c in content for c in ["退位", "借位", "29", "347"]):  # 可能有退位
                    q.knowledge_points.append(kp_map["退位减法"])
            elif "竖式" in content:
                # 综合计算
                q.knowledge_points.append(kp_map["两位数加减法"])
                q.knowledge_points.append(kp_map["进位加法"])
                q.knowledge_points.append(kp_map["退位减法"])
            else:
                # 默认
                q.knowledge_points.append(kp_map["两位数加减法"])

        db.commit()

        print(f"\n✓ 成功修正 {len(questions)} 道题目的知识点关联")

        # 验证
        print("\n验证结果:")
        for q in questions[:3]:
            kp_names = [kp.name for kp in q.knowledge_points]
            print(f"  题目: {q.content[:25]}...")
            print(f"    章节: {q.chapter}")
            print(f"    知识点: {kp_names}")

    except Exception as e:
        db.rollback()
        print(f"❌ 修正失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    fix_knowledge_points()
