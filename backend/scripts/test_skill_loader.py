"""
测试 Skill 加载器

用法：
python scripts/test_skill_loader.py
"""

import sys
import os

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.loader import SkillLoader


def test_skill_loader():
    """测试 Skill 加载器的各项功能"""

    print("\n" + "="*60)
    print("测试 Skill 加载器")
    print("="*60 + "\n")

    # 1. 初始化加载器
    print("测试 1: 初始化 SkillLoader")
    print("-" * 60)
    try:
        loader = SkillLoader()
        print("✓ SkillLoader 初始化成功\n")
    except Exception as e:
        print(f"❌ 初始化失败: {e}\n")
        return False

    # 2. 列出所有可用的 Skill
    print("测试 2: 列出所有 Skill")
    print("-" * 60)
    try:
        all_skills = loader.list_all_skills()
        print(f"发现 {len(all_skills)} 个 Skill:")
        for skill_name in all_skills:
            triggers = loader.get_skill_triggers(skill_name)
            print(f"  • {skill_name}")
            print(f"    触发词: {', '.join(triggers[:5])}")  # 只显示前5个
        print("\n✓ 列出 Skill 测试通过\n")
    except Exception as e:
        print(f"❌ 列出 Skill 失败: {e}\n")
        return False

    # 3. 测试根据关键词加载 Skill（出题场景）
    print("测试 3: 根据用户输入加载相关 Skill（出题场景）")
    print("-" * 60)
    test_inputs = [
        "帮我出份初二数学试卷",
        "生成一份期末考试",
        "我想搜索一些题目",
        "随便聊聊"  # 不应该匹配任何 Skill
    ]

    for user_input in test_inputs:
        print(f"\n用户输入: \"{user_input}\"")
        try:
            skills_content = loader.load_relevant_skills(user_input, max_skills=2)

            if skills_content:
                # 统计加载的 Skill 数量
                skill_count = skills_content.count("<skill name=")
                print(f"✓ 加载了 {skill_count} 个相关 Skill")

                # 显示前 200 个字符
                preview = skills_content[:200].replace("\n", " ")
                print(f"  内容预览: {preview}...")
            else:
                print("✓ 未匹配到相关 Skill（符合预期）")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False

    print("\n✓ 关键词匹配测试通过\n")

    # 4. 测试显式加载指定 Skill
    print("测试 4: 显式加载 exam_skill")
    print("-" * 60)
    try:
        exam_skill = loader.load_skill_by_name("exam_skill")

        if exam_skill:
            # 验证 Skill 结构
            checks = {
                "包含 <skill> 标签": "<skill name=" in exam_skill,
                "包含 Purpose 章节": "## Purpose" in exam_skill,
                "包含 Strategy 章节": "## Strategy" in exam_skill,
                "包含场景策略": "课后作业" in exam_skill and "单元测验" in exam_skill,
                "包含示例对话": "## Example" in exam_skill,
            }

            print("Skill 内容验证:")
            all_passed = True
            for check_name, result in checks.items():
                status = "✓" if result else "❌"
                print(f"  {status} {check_name}")
                if not result:
                    all_passed = False

            if all_passed:
                print("\n✓ exam_skill 内容结构正确\n")

                # 显示 Skill 统计信息
                lines = exam_skill.split("\n")
                print(f"Skill 统计:")
                print(f"  • 总行数: {len(lines)}")
                print(f"  • 总字符数: {len(exam_skill)}")
                print(f"  • 章节数: {exam_skill.count('##')}")

            else:
                print("\n❌ exam_skill 内容结构不完整\n")
                return False
        else:
            print("❌ 加载 exam_skill 失败（返回 None）\n")
            return False

    except Exception as e:
        print(f"❌ 加载 exam_skill 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False

    # 5. 测试 Skill 内容能否注入到 Prompt
    print("\n测试 5: Skill 内容注入到 System Prompt")
    print("-" * 60)
    try:
        user_input = "帮我出份初二数学单元测验"
        skills_content = loader.load_relevant_skills(user_input)

        # 构建完整的 System Prompt
        system_prompt = f"""
你是一个专业的 K12 出题助手。

{skills_content}

请根据上述 Skill 策略处理用户请求。
"""

        print(f"✓ System Prompt 构建成功")
        print(f"  • Prompt 总长度: {len(system_prompt)} 字符")
        print(f"  • 包含 Skill 内容: {len(skills_content)} 字符")
        print(f"  • Skill 占比: {len(skills_content)/len(system_prompt)*100:.1f}%")

        # 验证 Prompt 包含关键内容
        key_contents = [
            "Phase 1: 参数收集",
            "Phase 2: 场景策略匹配",
            "Phase 3: 题目获取",
            "Phase 4: 试卷组装"
        ]

        print("\n关键内容检查:")
        for content in key_contents:
            if content in system_prompt:
                print(f"  ✓ {content}")
            else:
                print(f"  ❌ {content}")
                return False

        print("\n✓ Skill 内容成功注入到 System Prompt\n")

    except Exception as e:
        print(f"❌ Prompt 注入测试失败: {e}\n")
        return False

    # 总结
    print("="*60)
    print("✅ Skill 加载器所有测试通过！")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = test_skill_loader()
    sys.exit(0 if success else 1)
