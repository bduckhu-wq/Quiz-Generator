"""
生成 Mock 测试数据

用法：
python scripts/generate_mock_data.py
"""

import sys
import os
import json
import random

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import SessionLocal
from models import Question, KnowledgePoint, Subject, Grade, QuestionType, Difficulty


# Mock 数据模板
MATH_KNOWLEDGE_POINTS = [
    "一元一次方程",
    "一元二次方程",  # 新增
    "二元一次方程组",
    "一次函数",
    "二次函数",
    "反比例函数",
    "正比例函数",  # 新增
    "三角形",
    "四边形",
    "圆",
    "勾股定理",
    "相似三角形",
    "全等三角形",
    "平行线",
    "不等式",
    "一元一次不等式",  # 新增
    "概率与统计",
    "平面直角坐标系",
    "有理数",  # 新增
    "实数",  # 新增
    "整式的加减",  # 新增
    "因式分解"  # 新增
]

PHYSICS_KNOWLEDGE_POINTS = [
    "力与运动",
    "牛顿三定律",
    "压强",
    "浮力",
    "杠杆",
    "功和功率",
    "机械能",
    "欧姆定律",
    "电功率",
    "串并联电路",
    "电磁感应",
    "光的反射",
    "光的折射",
    "声现象",
    "物态变化"
]

# 数学题目模板
MATH_QUESTIONS = [
    {
        "type": QuestionType.SINGLE_CHOICE,
        "content": "若方程 2x + 3 = 7 的解为 x = a，则 a 的值为（    ）",
        "options": json.dumps(["A. 1", "B. 2", "C. 3", "D. 4"], ensure_ascii=False),
        "answer": "B",
        "analysis": "移项得 2x = 4，两边同除以 2 得 x = 2",
        "kp": ["一元一次方程"]
    },
    {
        "type": QuestionType.SINGLE_CHOICE,
        "content": "下列函数中，y 随 x 的增大而增大的是（    ）",
        "options": json.dumps(["A. y = -2x", "B. y = 3x + 1", "C. y = -x + 5", "D. y = -0.5x"], ensure_ascii=False),
        "answer": "B",
        "analysis": "一次函数 y = kx + b 中，当 k > 0 时，y 随 x 增大而增大",
        "kp": ["一次函数"]
    },
    {
        "type": QuestionType.BLANK,
        "content": "若二次函数 y = x² - 4x + 3 的顶点坐标为 (______, ______)",
        "options": None,
        "answer": "(2, -1)",
        "analysis": "配方得 y = (x - 2)² - 1，顶点为 (2, -1)",
        "kp": ["二次函数"]
    },
    {
        "type": QuestionType.CALCULATION,
        "content": "解方程：3x - 2(x - 1) = 5",
        "options": None,
        "answer": "x = 3",
        "analysis": "去括号得 3x - 2x + 2 = 5，移项得 x = 3",
        "kp": ["一元一次方程"]
    },
    {
        "type": QuestionType.PROOF,
        "content": "已知：在 △ABC 中，AB = AC，D 是 BC 的中点。求证：AD ⊥ BC",
        "options": None,
        "answer": "证明：连接 AD。因为 AB = AC，D 是 BC 中点，所以 AD 是 BC 的垂直平分线，即 AD ⊥ BC",
        "analysis": "利用等腰三角形三线合一性质",
        "kp": ["三角形", "全等三角形"]
    },
    {
        "type": QuestionType.SINGLE_CHOICE,
        "content": "一元二次方程 x² - 5x + 6 = 0 的解为（    ）",
        "options": json.dumps(["A. x₁=2, x₂=3", "B. x₁=-2, x₂=-3", "C. x₁=1, x₂=6", "D. x₁=-1, x₂=-6"], ensure_ascii=False),
        "answer": "A",
        "analysis": "因式分解：(x-2)(x-3)=0，得 x₁=2, x₂=3",
        "kp": ["一元二次方程"]
    },
    {
        "type": QuestionType.CALCULATION,
        "content": "解方程：x² - 4x + 3 = 0",
        "options": None,
        "answer": "x₁=1, x₂=3",
        "analysis": "因式分解：(x-1)(x-3)=0，得 x₁=1, x₂=3",
        "kp": ["一元二次方程"]
    },
    {
        "type": QuestionType.BLANK,
        "content": "方程 x² + 2x - 8 = 0 的两个根的和为 ______，积为 ______",
        "options": None,
        "answer": "-2, -8",
        "analysis": "由韦达定理：x₁+x₂=-b/a=-2, x₁x₂=c/a=-8",
        "kp": ["一元二次方程"]
    }
]

PHYSICS_QUESTIONS = [
    {
        "type": QuestionType.SINGLE_CHOICE,
        "content": "关于力的作用效果，下列说法正确的是（    ）",
        "options": json.dumps([
            "A. 力可以改变物体的运动状态",
            "B. 力只能使物体发生形变",
            "C. 力只能改变物体的速度",
            "D. 力不能改变物体的形状"
        ], ensure_ascii=False),
        "answer": "A",
        "analysis": "力的作用效果有两个：改变物体运动状态和改变物体形状",
        "kp": ["力与运动"]
    },
    {
        "type": QuestionType.CALCULATION,
        "content": "一个物体在水平面上受到 10N 的拉力，在 5s 内移动了 20m，求拉力做的功和功率。",
        "options": None,
        "answer": "W = Fs = 10N × 20m = 200J；P = W/t = 200J / 5s = 40W",
        "analysis": "功 = 力 × 距离，功率 = 功 / 时间",
        "kp": ["功和功率"]
    },
    {
        "type": QuestionType.EXPERIMENT,
        "content": "探究串联电路电流特点的实验中，需要测量哪些物理量？使用什么仪器？",
        "options": None,
        "answer": "测量各点电流，使用电流表",
        "analysis": "串联电路中各处电流相等",
        "kp": ["串并联电路", "欧姆定律"]
    }
]


def create_knowledge_points(db):
    """创建知识点"""
    print("创建知识点数据...")

    kp_map = {}

    # 数学知识点
    for kp_name in MATH_KNOWLEDGE_POINTS:
        kp = KnowledgePoint(
            name=kp_name,
            subject=Subject.MATH,
            grade=Grade.GRADE_8,
            description=f"{kp_name}相关内容"
        )
        db.add(kp)
        db.flush()  # 获取 ID
        kp_map[kp_name] = kp

    # 物理知识点
    for kp_name in PHYSICS_KNOWLEDGE_POINTS:
        kp = KnowledgePoint(
            name=kp_name,
            subject=Subject.PHYSICS,
            grade=Grade.GRADE_8,
            description=f"{kp_name}相关内容"
        )
        db.add(kp)
        db.flush()
        kp_map[kp_name] = kp

    db.commit()
    print(f"✓ 创建了 {len(kp_map)} 个知识点\n")

    return kp_map


def create_questions(db, kp_map, count=100):
    """创建题目"""
    print(f"创建 {count} 道题目...")

    created_count = 0

    for i in range(count):
        # 随机选择学科
        if i % 2 == 0:
            subject = Subject.MATH
            templates = MATH_QUESTIONS
            kp_pool = MATH_KNOWLEDGE_POINTS
        else:
            subject = Subject.PHYSICS
            templates = PHYSICS_QUESTIONS
            kp_pool = PHYSICS_KNOWLEDGE_POINTS

        # 随机选择模板
        template = random.choice(templates)

        # 随机选择难度
        difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])

        # 随机选择年级
        grade = random.choice([Grade.GRADE_7, Grade.GRADE_8, Grade.GRADE_9])

        # 创建题目
        question = Question(
            subject=subject,
            grade=grade,
            question_type=template["type"],
            difficulty=difficulty,
            content=f"[第{i+1}题] {template['content']}",
            options=template["options"],
            answer=template["answer"],
            analysis=template["analysis"],
            default_score=random.choice([3, 5, 8, 10, 12]),
            source=f"模拟测试题库 #{i+1}"
        )

        # 关联知识点
        for kp_name in template["kp"]:
            if kp_name in kp_map:
                question.knowledge_points.append(kp_map[kp_name])

        db.add(question)
        created_count += 1

        # 每 20 条提交一次
        if (i + 1) % 20 == 0:
            db.commit()
            print(f"  已创建 {i+1}/{count} 道题目...")

    db.commit()
    print(f"✓ 创建了 {created_count} 道题目\n")

    return created_count


def main():
    """生成 Mock 数据"""
    print("\n" + "="*60)
    print("生成 Mock 测试数据")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_count = db.query(Question).count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有 {existing_count} 道题目")
            response = input("是否清空并重新生成？(y/n): ")
            if response.lower() != 'y':
                print("已取消")
                return False

            # 清空数据
            print("\n清空现有数据...")
            db.query(Question).delete()
            db.query(KnowledgePoint).delete()
            db.commit()
            print("✓ 清空完成\n")

        # 1. 创建知识点
        kp_map = create_knowledge_points(db)

        # 2. 创建题目
        question_count = create_questions(db, kp_map, count=100)

        # 3. 验证数据
        print("验证数据...")
        total_questions = db.query(Question).count()
        total_kp = db.query(KnowledgePoint).count()

        print(f"✓ 数据库中共有:")
        print(f"  • 题目: {total_questions} 道")
        print(f"  • 知识点: {total_kp} 个")

        # 统计各学科题目数
        math_count = db.query(Question).filter(Question.subject == Subject.MATH).count()
        physics_count = db.query(Question).filter(Question.subject == Subject.PHYSICS).count()

        print(f"\n按学科分布:")
        print(f"  • 数学: {math_count} 道")
        print(f"  • 物理: {physics_count} 道")

        print("\n" + "="*60)
        print("✅ Mock 数据生成完成！")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ 生成失败: {e}\n")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
