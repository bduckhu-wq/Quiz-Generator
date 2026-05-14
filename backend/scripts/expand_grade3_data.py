"""
扩充三年级数学题库到50道
涵盖多个章节和知识点
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import SessionLocal
from models.question import Question, KnowledgePoint
from models.enums import Subject, Grade, QuestionType, Difficulty
import uuid


def expand_questions():
    """扩充三年级题库"""
    db = SessionLocal()

    try:
        print("开始扩充三年级数学题库...")
        print("="*70)

        # 1. 创建章节对应的知识点
        knowledge_points_data = [
            # 第一章：两位数乘一位数
            {"name": "两位数乘一位数", "chapter": "第一章", "description": "两位数与一位数的乘法运算"},
            {"name": "乘法估算", "chapter": "第一章", "description": "乘法的估算方法"},

            # 第二章：除法
            {"name": "除法基础", "chapter": "第二章", "description": "除法的意义和基本运算"},
            {"name": "有余数的除法", "chapter": "第二章", "description": "带余数的除法运算"},

            # 第三章：加减法（已有，补充）
            {"name": "三位数加减法", "chapter": "第三章", "description": "三位数的加减运算"},

            # 第四章：长度单位
            {"name": "长度单位换算", "chapter": "第四章", "description": "米、分米、厘米、毫米的换算"},
            {"name": "长度计算", "chapter": "第四章", "description": "长度的加减计算"},

            # 第五章：面积
            {"name": "面积认识", "chapter": "第五章", "description": "面积的初步认识"},
            {"name": "正方形面积", "chapter": "第五章", "description": "正方形面积的计算"},
            {"name": "长方形面积", "chapter": "第五章", "description": "长方形面积的计算"},

            # 第六章：时间
            {"name": "时间单位", "chapter": "第六章", "description": "时、分、秒的认识"},
            {"name": "时间计算", "chapter": "第六章", "description": "时间的加减计算"},

            # 第七章：分数初步
            {"name": "分数认识", "chapter": "第七章", "description": "简单分数的初步认识"},
            {"name": "分数比较", "chapter": "第七章", "description": "简单分数的大小比较"},

            # 第八章：重量
            {"name": "重量单位", "chapter": "第八章", "description": "千克、克的认识"},
            {"name": "重量计算", "chapter": "第八章", "description": "重量的加减计算"},
        ]

        # 创建知识点
        kp_map = {}
        for kp_data in knowledge_points_data:
            # 检查是否已存在
            existing = db.query(KnowledgePoint).filter(
                KnowledgePoint.name == kp_data["name"],
                KnowledgePoint.grade == Grade.GRADE_3
            ).first()

            if not existing:
                kp = KnowledgePoint(
                    name=kp_data["name"],
                    subject=Subject.MATH,
                    grade=Grade.GRADE_3,
                    description=kp_data["description"]
                )
                db.add(kp)
                db.flush()
                kp_map[kp_data["name"]] = kp
                print(f"✓ 创建知识点: {kp.name}")
            else:
                kp_map[kp_data["name"]] = existing

        # 2. 创建题目
        questions_data = [
            # ===== 第一章：两位数乘一位数 (8题) =====
            {
                "chapter": "第一章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "12 × 3 = ?",
                "options": ["A. 36", "B. 35", "C. 34", "D. 33"],
                "answer": "A",
                "analysis": "12 × 3 = 36",
                "score": 5,
                "kps": ["两位数乘一位数"]
            },
            {
                "chapter": "第一章第一节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "计算：23 × 4 = ?",
                "options": None,
                "answer": "92",
                "analysis": "23 × 4 = 92",
                "score": 6,
                "kps": ["两位数乘一位数"]
            },
            {
                "chapter": "第一章第二节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.MEDIUM,
                "content": "48 × 5 最接近下面哪个数？",
                "options": ["A. 200", "B. 250", "C. 300", "D. 350"],
                "answer": "B",
                "analysis": "48 约等于 50，50 × 5 = 250",
                "score": 6,
                "kps": ["乘法估算"]
            },
            {
                "chapter": "第一章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "一本书有34页，小明每天看3页，他5天能看完吗？",
                "options": None,
                "answer": "不能",
                "analysis": "34 ÷ 3 ≈ 11天，5天看不完",
                "score": 8,
                "kps": ["两位数乘一位数", "除法基础"]
            },
            {
                "chapter": "第一章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "15 × 4 = ____",
                "options": None,
                "answer": "60",
                "analysis": "15 × 4 = 60",
                "score": 5,
                "kps": ["两位数乘一位数"]
            },
            {
                "chapter": "第一章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "一个篮球42元，买6个需要____元。",
                "options": None,
                "answer": "252",
                "analysis": "42 × 6 = 252（元）",
                "score": 6,
                "kps": ["两位数乘一位数"]
            },
            {
                "chapter": "第一章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "商店有28盒牛奶，每盒8元。如果全部卖出，能收入多少元？",
                "options": None,
                "answer": "224元",
                "analysis": "28 × 8 = 224（元）",
                "score": 8,
                "kps": ["两位数乘一位数"]
            },
            {
                "chapter": "第一章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "下列算式中，结果最大的是？",
                "options": ["A. 21 × 3", "B. 19 × 4", "C. 16 × 5", "D. 14 × 6"],
                "answer": "D",
                "analysis": "A=63, B=76, C=80, D=84，D最大",
                "score": 5,
                "kps": ["两位数乘一位数"]
            },

            # ===== 第二章：除法 (7题) =====
            {
                "chapter": "第二章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "48 ÷ 6 = ?",
                "options": ["A. 6", "B. 7", "C. 8", "D. 9"],
                "answer": "C",
                "analysis": "48 ÷ 6 = 8",
                "score": 5,
                "kps": ["除法基础"]
            },
            {
                "chapter": "第二章第二节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.MEDIUM,
                "content": "25 ÷ 4 = 6 余几？",
                "options": ["A. 1", "B. 2", "C. 3", "D. 4"],
                "answer": "A",
                "analysis": "25 ÷ 4 = 6...1",
                "score": 6,
                "kps": ["有余数的除法"]
            },
            {
                "chapter": "第二章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "56 ÷ 7 = ____",
                "options": None,
                "answer": "8",
                "analysis": "56 ÷ 7 = 8",
                "score": 5,
                "kps": ["除法基础"]
            },
            {
                "chapter": "第二章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "43 ÷ 5 = ____ 余 ____",
                "options": None,
                "answer": "8 余 3",
                "analysis": "43 ÷ 5 = 8...3",
                "score": 6,
                "kps": ["有余数的除法"]
            },
            {
                "chapter": "第二章第一节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "72个苹果平均分给9个小朋友，每人分几个？",
                "options": None,
                "answer": "8个",
                "analysis": "72 ÷ 9 = 8（个）",
                "score": 8,
                "kps": ["除法基础"]
            },
            {
                "chapter": "第二章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "有35块巧克力，每5块装一盒，能装几盒？",
                "options": None,
                "answer": "7盒",
                "analysis": "35 ÷ 5 = 7（盒）",
                "score": 8,
                "kps": ["除法基础"]
            },
            {
                "chapter": "第二章第二节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "计算：\n(1) 64 ÷ 8\n(2) 50 ÷ 7",
                "options": None,
                "answer": "(1) 8\n(2) 7 余 1",
                "analysis": "(1) 64 ÷ 8 = 8\n(2) 50 ÷ 7 = 7...1",
                "score": 8,
                "kps": ["除法基础", "有余数的除法"]
            },

            # ===== 第三章：三位数加减法 (5题) =====
            {
                "chapter": "第三章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "356 + 278 = ?",
                "options": ["A. 624", "B. 634", "C. 644", "D. 654"],
                "answer": "B",
                "analysis": "356 + 278 = 634",
                "score": 5,
                "kps": ["三位数加减法"]
            },
            {
                "chapter": "第三章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "800 - 367 = ____",
                "options": None,
                "answer": "433",
                "analysis": "800 - 367 = 433",
                "score": 6,
                "kps": ["三位数加减法"]
            },
            {
                "chapter": "第三章第二节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "竖式计算：\n(1) 456 + 387\n(2) 702 - 458",
                "options": None,
                "answer": "(1) 843\n(2) 244",
                "analysis": "(1) 456 + 387 = 843\n(2) 702 - 458 = 244",
                "score": 8,
                "kps": ["三位数加减法"]
            },
            {
                "chapter": "第三章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "图书馆有故事书456本，科技书387本。两种书一共有多少本？",
                "options": None,
                "answer": "843本",
                "analysis": "456 + 387 = 843（本）",
                "score": 8,
                "kps": ["三位数加减法"]
            },
            {
                "chapter": "第三章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "500 + 299 = ____",
                "options": None,
                "answer": "799",
                "analysis": "500 + 299 = 799",
                "score": 5,
                "kps": ["三位数加减法"]
            },

            # ===== 第四章：长度单位 (6题) =====
            {
                "chapter": "第四章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "1米 = 多少厘米？",
                "options": ["A. 10厘米", "B. 50厘米", "C. 100厘米", "D. 1000厘米"],
                "answer": "C",
                "analysis": "1米 = 100厘米",
                "score": 5,
                "kps": ["长度单位换算"]
            },
            {
                "chapter": "第四章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "5米 = ____ 厘米",
                "options": None,
                "answer": "500",
                "analysis": "5米 = 5 × 100 = 500厘米",
                "score": 6,
                "kps": ["长度单位换算"]
            },
            {
                "chapter": "第四章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "一根绳子长3米，用去120厘米，还剩____厘米。",
                "options": None,
                "answer": "180",
                "analysis": "3米 = 300厘米，300 - 120 = 180（厘米）",
                "score": 7,
                "kps": ["长度单位换算", "长度计算"]
            },
            {
                "chapter": "第四章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "小明身高1米35厘米，小红身高1米42厘米。小红比小明高多少厘米？",
                "options": None,
                "answer": "7厘米",
                "analysis": "142 - 135 = 7（厘米）",
                "score": 8,
                "kps": ["长度计算"]
            },
            {
                "chapter": "第四章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "1分米 = 多少厘米？",
                "options": ["A. 5厘米", "B. 10厘米", "C. 15厘米", "D. 20厘米"],
                "answer": "B",
                "analysis": "1分米 = 10厘米",
                "score": 5,
                "kps": ["长度单位换算"]
            },
            {
                "chapter": "第四章第二节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "计算：\n(1) 2米40厘米 + 1米80厘米\n(2) 5米 - 2米35厘米",
                "options": None,
                "answer": "(1) 4米20厘米\n(2) 2米65厘米",
                "analysis": "(1) 240 + 180 = 420厘米 = 4米20厘米\n(2) 500 - 235 = 265厘米 = 2米65厘米",
                "score": 10,
                "kps": ["长度单位换算", "长度计算"]
            },

            # ===== 第五章：面积 (6题) =====
            {
                "chapter": "第五章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "边长是5厘米的正方形，面积是多少平方厘米？",
                "options": ["A. 10", "B. 20", "C. 25", "D. 30"],
                "answer": "C",
                "analysis": "正方形面积 = 边长 × 边长 = 5 × 5 = 25（平方厘米）",
                "score": 5,
                "kps": ["正方形面积"]
            },
            {
                "chapter": "第五章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "长方形长8厘米，宽5厘米，面积是____平方厘米。",
                "options": None,
                "answer": "40",
                "analysis": "长方形面积 = 长 × 宽 = 8 × 5 = 40（平方厘米）",
                "score": 6,
                "kps": ["长方形面积"]
            },
            {
                "chapter": "第五章第一节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "一个正方形花坛，边长6米，它的面积是多少平方米？",
                "options": None,
                "answer": "36平方米",
                "analysis": "6 × 6 = 36（平方米）",
                "score": 8,
                "kps": ["正方形面积"]
            },
            {
                "chapter": "第五章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "教室长10米，宽7米。教室的面积是多少平方米？",
                "options": None,
                "answer": "70平方米",
                "analysis": "10 × 7 = 70（平方米）",
                "score": 10,
                "kps": ["长方形面积"]
            },
            {
                "chapter": "第五章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "正方形的边长是4厘米，面积是____平方厘米。",
                "options": None,
                "answer": "16",
                "analysis": "4 × 4 = 16（平方厘米）",
                "score": 5,
                "kps": ["正方形面积"]
            },
            {
                "chapter": "第五章第二节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "计算下列图形的面积：\n(1) 正方形，边长7厘米\n(2) 长方形，长12厘米，宽3厘米",
                "options": None,
                "answer": "(1) 49平方厘米\n(2) 36平方厘米",
                "analysis": "(1) 7 × 7 = 49（平方厘米）\n(2) 12 × 3 = 36（平方厘米）",
                "score": 10,
                "kps": ["正方形面积", "长方形面积"]
            },

            # ===== 第六章：时间 (6题) =====
            {
                "chapter": "第六章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "1小时 = 多少分钟？",
                "options": ["A. 30分钟", "B. 50分钟", "C. 60分钟", "D. 100分钟"],
                "answer": "C",
                "analysis": "1小时 = 60分钟",
                "score": 5,
                "kps": ["时间单位"]
            },
            {
                "chapter": "第六章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "1分钟 = ____ 秒",
                "options": None,
                "answer": "60",
                "analysis": "1分钟 = 60秒",
                "score": 5,
                "kps": ["时间单位"]
            },
            {
                "chapter": "第六章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "小明8:00出发去学校，8:25到达，他在路上用了____分钟。",
                "options": None,
                "answer": "25",
                "analysis": "8:25 - 8:00 = 25分钟",
                "score": 6,
                "kps": ["时间计算"]
            },
            {
                "chapter": "第六章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "电影从下午2:30开始，放映了120分钟，几点结束？",
                "options": None,
                "answer": "4:30",
                "analysis": "120分钟 = 2小时，2:30 + 2小时 = 4:30",
                "score": 8,
                "kps": ["时间单位", "时间计算"]
            },
            {
                "chapter": "第六章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "2小时 = 多少分钟？",
                "options": ["A. 100分钟", "B. 110分钟", "C. 120分钟", "D. 130分钟"],
                "answer": "C",
                "analysis": "2小时 = 2 × 60 = 120分钟",
                "score": 5,
                "kps": ["时间单位"]
            },
            {
                "chapter": "第六章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.HARD,
                "content": "小红做作业用了45分钟，做完作业后又看了30分钟的书。她一共用了多长时间？",
                "options": None,
                "answer": "1小时15分钟",
                "analysis": "45 + 30 = 75分钟 = 1小时15分钟",
                "score": 10,
                "kps": ["时间计算"]
            },

            # ===== 第七章：分数初步 (6题) =====
            {
                "chapter": "第七章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "把一个苹果平均分成2份，每份是这个苹果的？",
                "options": ["A. 1/2", "B. 1/3", "C. 1/4", "D. 2/3"],
                "answer": "A",
                "analysis": "平均分成2份，每份是1/2",
                "score": 5,
                "kps": ["分数认识"]
            },
            {
                "chapter": "第七章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "把一个西瓜平均分成4份，每份是这个西瓜的____。",
                "options": None,
                "answer": "1/4",
                "analysis": "平均分成4份，每份是1/4",
                "score": 5,
                "kps": ["分数认识"]
            },
            {
                "chapter": "第七章第二节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.MEDIUM,
                "content": "比较大小：1/2 ○ 1/3",
                "options": ["A. >", "B. <", "C. =", "D. 无法比较"],
                "answer": "A",
                "analysis": "分母相同时，分子大的分数大；分子相同时，分母小的分数大。1/2 > 1/3",
                "score": 6,
                "kps": ["分数比较"]
            },
            {
                "chapter": "第七章第一节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "一根绳子长8米，用去了1/4，用去了多少米？",
                "options": None,
                "answer": "2米",
                "analysis": "8 × 1/4 = 2（米）",
                "score": 8,
                "kps": ["分数认识"]
            },
            {
                "chapter": "第七章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "在括号里填上 > 、< 或 =：\n1/3 ____  1/5",
                "options": None,
                "answer": ">",
                "analysis": "分子相同，分母小的分数大，1/3 > 1/5",
                "score": 6,
                "kps": ["分数比较"]
            },
            {
                "chapter": "第七章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "把一个蛋糕平均分成8份，吃了3份，还剩几分之几？",
                "options": ["A. 3/8", "B. 5/8", "C. 3/5", "D. 5/3"],
                "answer": "B",
                "analysis": "还剩 (8-3)/8 = 5/8",
                "score": 5,
                "kps": ["分数认识"]
            },

            # ===== 第八章：重量 (6题) =====
            {
                "chapter": "第八章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "1千克 = 多少克？",
                "options": ["A. 100克", "B. 500克", "C. 1000克", "D. 10000克"],
                "answer": "C",
                "analysis": "1千克 = 1000克",
                "score": 5,
                "kps": ["重量单位"]
            },
            {
                "chapter": "第八章第一节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.EASY,
                "content": "3千克 = ____ 克",
                "options": None,
                "answer": "3000",
                "analysis": "3千克 = 3 × 1000 = 3000克",
                "score": 5,
                "kps": ["重量单位"]
            },
            {
                "chapter": "第八章第二节",
                "question_type": QuestionType.BLANK,
                "difficulty": Difficulty.MEDIUM,
                "content": "一袋大米重5千克，买3袋一共重____千克。",
                "options": None,
                "answer": "15",
                "analysis": "5 × 3 = 15（千克）",
                "score": 6,
                "kps": ["重量计算"]
            },
            {
                "chapter": "第八章第二节",
                "question_type": QuestionType.APPLICATION,
                "difficulty": Difficulty.MEDIUM,
                "content": "一个西瓜重4千克500克，一个哈密瓜重2千克800克。西瓜比哈密瓜重多少克？",
                "options": None,
                "answer": "1700克",
                "analysis": "4500 - 2800 = 1700（克）",
                "score": 8,
                "kps": ["重量单位", "重量计算"]
            },
            {
                "chapter": "第八章第一节",
                "question_type": QuestionType.SINGLE_CHOICE,
                "difficulty": Difficulty.EASY,
                "content": "2000克 = 多少千克？",
                "options": ["A. 1千克", "B. 2千克", "C. 3千克", "D. 4千克"],
                "answer": "B",
                "analysis": "2000克 = 2千克",
                "score": 5,
                "kps": ["重量单位"]
            },
            {
                "chapter": "第八章第二节",
                "question_type": QuestionType.CALCULATION,
                "difficulty": Difficulty.HARD,
                "content": "计算：\n(1) 3千克400克 + 2千克800克\n(2) 5千克 - 1千克600克",
                "options": None,
                "answer": "(1) 6千克200克\n(2) 3千克400克",
                "analysis": "(1) 3400 + 2800 = 6200克 = 6千克200克\n(2) 5000 - 1600 = 3400克 = 3千克400克",
                "score": 10,
                "kps": ["重量单位", "重量计算"]
            },
        ]

        print(f"\n开始创建 {len(questions_data)} 道题目...")
        print("-"*70)

        created_count = 0
        for idx, q_data in enumerate(questions_data, 1):
            # 转换options为JSON字符串
            if q_data["options"]:
                options_json = json.dumps(q_data["options"])
            else:
                options_json = None

            # 创建题目
            q = Question(
                id=str(uuid.uuid4()),
                subject=Subject.MATH,
                grade=Grade.GRADE_3,
                question_type=q_data["question_type"],
                difficulty=q_data["difficulty"],
                content=q_data["content"],
                options=options_json,
                answer=q_data["answer"],
                analysis=q_data["analysis"],
                default_score=q_data["score"],
                source="课后练习",
                chapter=q_data["chapter"]
            )
            db.add(q)
            db.flush()

            # 关联知识点
            for kp_name in q_data["kps"]:
                if kp_name in kp_map:
                    q.knowledge_points.append(kp_map[kp_name])

            created_count += 1
            if created_count % 10 == 0:
                print(f"已创建 {created_count}/{len(questions_data)} 道题目...")

        db.commit()

        print("\n" + "="*70)
        print(f"✅ 扩充完成！")
        print(f"  新增知识点: {len(knowledge_points_data)} 个")
        print(f"  新增题目: {len(questions_data)} 道")

        # 统计总数
        total_questions = db.query(Question).filter(Question.grade == Grade.GRADE_3).count()
        total_kps = db.query(KnowledgePoint).filter(KnowledgePoint.grade == Grade.GRADE_3).count()

        print(f"\n三年级题库总览:")
        print(f"  总题目数: {total_questions} 道")
        print(f"  总知识点: {total_kps} 个")

        # 按章节统计
        print(f"\n按章节分布:")
        chapters = ["第一章", "第二章", "第三章", "第四章", "第五章", "第六章", "第七章", "第八章"]
        for chapter in chapters:
            count = db.query(Question).filter(
                Question.grade == Grade.GRADE_3,
                Question.chapter.like(f"{chapter}%")
            ).count()
            print(f"  {chapter}: {count} 道")

    except Exception as e:
        db.rollback()
        print(f"❌ 扩充失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    expand_questions()
