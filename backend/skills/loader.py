"""
Skill 加载器 - OpenClaw 模式
渐进式加载 Skill 文档到 System Prompt
"""

import re
import json
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.llm_service import LLMService


class SkillLoader:
    """
    OpenClaw 式的 Skill 加载器

    功能：
    1. 根据用户输入动态加载相关 Skill
    2. 避免一次性加载所有 Skill 占满 Context
    3. 支持 Skill 版本管理
    """

    def __init__(self, skills_dir: str = None):
        # 如果未指定，自动找到 skills 目录（相对于此文件）
        if skills_dir is None:
            skills_dir = Path(__file__).parent
        else:
            skills_dir = Path(skills_dir)

        self.skills_dir = skills_dir
        self.skill_index = self._build_index()

    def _build_index(self) -> dict:
        """
        构建 Skill 索引

        Returns:
            {
                "exam_skill": {
                    "file": Path("exam_skill.md"),
                    "triggers": ["出题", "生成试卷", ...],
                    "purpose": "帮助教师生成试卷...",
                    "content": "..."
                }
            }
        """
        index = {}

        for skill_file in self.skills_dir.glob("*.md"):
            content = skill_file.read_text(encoding='utf-8')

            # 提取 <skill> 标签属性
            match = re.search(
                r'<skill\s+name="([^"]+)"\s+trigger="([^"]+)">',
                content
            )

            if match:
                name = match.group(1)
                triggers = match.group(2).split("|")

                # 提取 Purpose 章节（用于 LLM 理解 Skill 用途）
                purpose_match = re.search(
                    r'## Purpose\s*\n(.+?)(?=\n##|\Z)',
                    content,
                    re.DOTALL
                )
                purpose = purpose_match.group(1).strip() if purpose_match else "无描述"

                index[name] = {
                    "file": skill_file,
                    "triggers": triggers,
                    "purpose": purpose,
                    "content": content
                }

        return index

    def load_relevant_skills(
        self,
        user_input: str,
        max_skills: int = 2
    ) -> str:
        """
        根据用户输入加载相关 Skill

        Args:
            user_input: 用户输入文本
            max_skills: 最多加载几个 Skill（避免 Context 爆炸）

        Returns:
            拼接后的 Skill 内容（<skills>...</skills> 格式）

        Example:
            user_input = "帮我出份初二数学试卷"
            → 匹配到 "exam_skill" (trigger: "出题|生成试卷")
            → 返回 exam_skill.md 的内容
        """
        matched_skills = []

        # 遍历所有 Skill，检查是否匹配 trigger
        for name, info in self.skill_index.items():
            for trigger in info["triggers"]:
                if trigger in user_input:
                    matched_skills.append((name, info))
                    break  # 避免重复添加

        # 限制数量（按匹配顺序取前 N 个）
        matched_skills = matched_skills[:max_skills]

        if not matched_skills:
            return ""

        # 拼接 Skill 内容
        skills_content = "<skills>\n\n"
        for name, info in matched_skills:
            skills_content += info["content"] + "\n\n"
        skills_content += "</skills>"

        return skills_content

    def load_skill_by_name(self, skill_name: str) -> Optional[str]:
        """
        显式加载指定 Skill

        Args:
            skill_name: Skill 名称（如 "exam_skill"）

        Returns:
            Skill 内容，如果不存在返回 None
        """
        if skill_name in self.skill_index:
            return self.skill_index[skill_name]["content"]
        return None

    def list_all_skills(self) -> list[str]:
        """列出所有可用的 Skill 名称"""
        return list(self.skill_index.keys())

    def get_skill_triggers(self, skill_name: str) -> list[str]:
        """获取指定 Skill 的触发词列表"""
        if skill_name in self.skill_index:
            return self.skill_index[skill_name]["triggers"]
        return []

    def _build_skill_catalog(self) -> str:
        """
        构建 Skill 目录（用于 LLM 路由）

        Returns:
            Skill 清单文本，包含名称、用途、触发词示例
        """
        catalog = "可用的 Skills:\n\n"

        for idx, (name, info) in enumerate(self.skill_index.items(), 1):
            catalog += f"{idx}. **{name}**\n"
            catalog += f"   用途: {info['purpose']}\n"
            catalog += f"   示例: {', '.join(info['triggers'][:3])}\n\n"

        return catalog

    async def route_to_skill(
        self,
        user_input: str,
        llm_service: "LLMService"
    ) -> str:
        """
        基于 LLM 的智能 Skill 路由

        Args:
            user_input: 用户输入文本
            llm_service: LLM 服务实例

        Returns:
            加载的 Skill 内容（<skills>...</skills> 格式）
            如果无需 Skill 返回空字符串

        Example:
            user_input = "出3道题"
            → LLM 识别为出题意图
            → 返回 exam_skill.md 的内容
        """
        # 1. 构建 Skill 目录
        skill_catalog = self._build_skill_catalog()

        # 2. 调用 LLM 进行意图识别
        system_prompt = f"""你是一个 Skill 路由助手。

{skill_catalog}

**任务**：根据用户输入，判断需要哪个 Skill。

**输出格式**（必须严格遵守 JSON 格式）：
{{
    "skill_name": "exam_skill" | "search_skill" | "none",
    "reason": "选择理由（简短说明）"
}}

**规则**：
- 如果用户想出题、生成试卷、组卷 → exam_skill
- 如果用户想搜题、查找题目、检索 → search_skill
- 如果是闲聊、无明确意图 → none

**重要**：只返回 JSON，不要有其他文字。"""

        try:
            response = await llm_service.chat(
                messages=[{"role": "user", "content": user_input}],
                system_prompt=system_prompt,
                stream=False
            )

            # 3. 解析 LLM 响应
            content = response.content.strip()

            # 尝试提取 JSON（可能包含 markdown 代码块）
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                skill_name = result.get("skill_name", "none")

                # 4. 加载对应 Skill
                if skill_name != "none" and skill_name in self.skill_index:
                    skill_content = self.skill_index[skill_name]["content"]
                    return f"<skills>\n\n{skill_content}\n\n</skills>"

            return ""

        except Exception as e:
            # 降级：LLM 失败时回退到关键词匹配
            print(f"⚠️  LLM 路由失败（{e}），回退到关键词匹配")
            return self.load_relevant_skills(user_input)


# 使用示例
if __name__ == "__main__":
    loader = SkillLoader()

    # 示例 1：根据用户输入加载
    user_input = "帮我出份初二数学单元测验"
    skills = loader.load_relevant_skills(user_input)
    print("加载的 Skills:")
    print(skills[:200])  # 打印前 200 字符

    # 示例 2：列出所有 Skill
    print("\n所有可用 Skills:")
    print(loader.list_all_skills())

    # 示例 3：查看 Skill 触发词
    print("\nexam_skill 的触发词:")
    print(loader.get_skill_triggers("exam_skill"))
