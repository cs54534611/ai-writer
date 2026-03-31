"""AI 审查服务 - 矛盾检测/OOC/敏感词"""

import re
from typing import TypedDict, Optional

from src.services.llm import get_llm_service, BaseLLMService


class ReviewIssue(TypedDict):
    """审查问题"""
    type: str  # 'contradiction' | 'ooc' | 'sensitive'
    severity: str  # 'low' | 'medium' | 'high'
    location: str  # 位置描述
    description: str  # 问题描述
    suggestion: str  # 修改建议


class ReviewResult(TypedDict):
    """审查结果"""
    score: float  # 0.0-10.0
    issues: list[ReviewIssue]
    stats: dict  # 字数/章节数/角色数等统计


class ReviewService:
    """审查服务"""

    # 内置敏感词库（简化版示例词）
    _SENSITIVE_WORDS = {
        'political': [
            '独裁', '专制', '暴政', '反动', '叛国',
            '颠覆', '渗透', '分裂', '台独', '藏独',
        ],
        'adult': [
            '色情', '淫秽', '嫖娼', '卖淫', '猥亵',
            '强奸', '性交', '裸体', '裸露', '色情',
        ],
        'violence': [
            '杀人', '谋杀', '屠杀', '虐杀', '暴击',
            '血洗', '炸毁', '行凶', '恐怖',
        ],
    }

    def __init__(self, llm_service: Optional[BaseLLMService] = None):
        """初始化审查服务"""
        self._llm_service = llm_service

    @property
    def llm(self) -> BaseLLMService:
        """获取 LLM 服务实例（懒加载）"""
        if self._llm_service is None:
            self._llm_service = get_llm_service()
        return self._llm_service

    def _load_sensitive_words(self) -> dict:
        """加载内置敏感词库"""
        return self._SENSITIVE_WORDS.copy()

    async def review_chapter(
        self,
        project_id: str,
        chapter_content: str,
        characters: list[dict],
        world_settings: list[dict],
    ) -> ReviewResult:
        """综合审查章节"""
        all_issues: list[ReviewIssue] = []

        # 1. 敏感词检测（本地）
        sensitive_issues = self.check_sensitive_words(chapter_content)
        all_issues.extend(sensitive_issues)

        # 2. OOC 检测（需要角色设定）
        for character in characters:
            ooc_issues = await self.detect_ooc(chapter_content, character)
            all_issues.extend(ooc_issues)

        # 3. 矛盾检测（简化版：基于关键词）
        contradiction_issues = self.detect_contradictions(
            project_id, chapter_content, ""
        )
        all_issues.extend(contradiction_issues)

        # 计算综合评分
        score = self._calculate_score(all_issues)

        # 统计信息
        stats = {
            'char_count': len(chapter_content),
            'word_count': len(chapter_content.replace('\n', '').split()),
            'char_count_in_chars': len(chapter_content),
            'character_count': len(characters),
            'world_setting_count': len(world_settings),
            'issue_count': len(all_issues),
            'issue_breakdown': {
                'contradiction': sum(1 for i in all_issues if i['type'] == 'contradiction'),
                'ooc': sum(1 for i in all_issues if i['type'] == 'ooc'),
                'sensitive': sum(1 for i in all_issues if i['type'] == 'sensitive'),
            }
        }

        return ReviewResult(
            score=score,
            issues=all_issues,
            stats=stats
        )

    def detect_contradictions(
        self,
        project_id: str,
        new_content: str,
        existing_content: str = "",
    ) -> list[ReviewIssue]:
        """检测前后矛盾：
        - 人物特征矛盾（年龄/外貌/性别）
        - 关系状态矛盾（敌人→朋友无过渡）
        - 时间线矛盾
        - 物品/能力矛盾
        """
        issues: list[ReviewIssue] = []

        # 简化版：基于关键词匹配检测矛盾
        # 1. 检测性别矛盾
        gender_patterns = [
            (r'\b(他|他的|男人|男孩|男性|先生|帅哥|老爸|父亲|儿子|兄弟)\b.*\b(她|她的|女人|女孩|女性|小姐|美女|老妈|母亲|女儿|姐妹)\b'),
            (r'\b(她|她的|女人|女孩|女性|小姐|美女|老妈|母亲|女儿|姐妹)\b.*\b(他|他的|男人|男孩|男性|先生|帅哥|老爸|父亲|儿子|兄弟)\b'),
        ]
        for pattern in gender_patterns:
            matches = list(re.finditer(pattern, new_content))
            if matches:
                for match in matches:
                    issues.append(ReviewIssue(
                        type='contradiction',
                        severity='high',
                        location=f"位置 {match.start()}-{match.end()}",
                        description="检测到性别描述矛盾（男性/女性代词混用）",
                        suggestion="统一使用一致的性别代词"
                    ))

        # 2. 检测时间线矛盾（简化版：检测明显的时间状语冲突）
        # 例如：先说"昨天"，又说"明天"
        time_words = ['昨天', '今天', '明天', '后天', '前天']
        found_times = [w for w in time_words if w in new_content]
        if len(found_times) > 1:
            # 检测在相邻段落中是否出现矛盾时间词
            paragraphs = new_content.split('\n\n')
            for i in range(len(paragraphs) - 1):
                p1_times = [w for w in time_words if w in paragraphs[i]]
                p2_times = [w for w in time_words if w in paragraphs[i + 1]]
                # 检测明显矛盾：昨天vs明天，今天vs后天等
                contradictions = [
                    ('昨天', '明天'), ('今天', '后天'), ('前天', '后天'),
                    ('昨天', '今天'), ('今天', '明天'),
                ]
                for t1, t2 in contradictions:
                    if t1 in p1_times and t2 in p2_times:
                        issues.append(ReviewIssue(
                            type='contradiction',
                            severity='medium',
                            location=f"第 {i+1} 段与第 {i+2} 段",
                            description=f"时间线矛盾：前一段提到'{t1}'，后一段提到'{t2}'",
                            suggestion="检查时间顺序是否正确"
                        ))

        # 3. 检测年龄矛盾（简化版）
        age_pattern = r'(\d+)(岁|多岁)'
        ages = re.findall(age_pattern, new_content)
        if len(ages) > 1:
            age_values = [int(a[0]) for a in ages]
            if len(set(age_values)) > 1:
                max_diff = max(age_values) - min(age_values)
                if max_diff > 10:  # 年龄差异超过10岁可能是矛盾
                    issues.append(ReviewIssue(
                        type='contradiction',
                        severity='medium',
                        location="全文",
                        description=f"检测到多个不同的年龄数值：{age_values}",
                        suggestion="检查角色年龄是否一致"
                    ))

        # 4. 检测关系状态矛盾（简化版：检测敌人/朋友关键词）
        enemy_words = ['敌人', '仇人', '憎恨', '仇恨', '敌对', '对立', '对抗']
        friend_words = ['朋友', '好友', '知己', '闺蜜', '兄弟', '姐妹', '挚友']
        
        has_enemy = any(w in new_content for w in enemy_words)
        has_friend = any(w in new_content for w in friend_words)
        
        if has_enemy and has_friend:
            # 简化检测：检测是否在描述同一个关系
            paragraphs = new_content.split('\n\n')
            for i, p in enumerate(paragraphs):
                p_enemy = any(w in p for w in enemy_words)
                p_friend = any(w in p for w in friend_words)
                if p_enemy and p_friend:
                    issues.append(ReviewIssue(
                        type='contradiction',
                        severity='high',
                        location=f"第 {i+1} 段",
                        description="同一段落中同时出现敌对和友好关系的描述",
                        suggestion="检查角色关系描述是否一致"
                    ))

        return issues

    async def detect_ooc(
        self,
        content: str,
        character: dict,
    ) -> list[ReviewIssue]:
        """检测角色 OOC（Out Of Character）：
        - AI 分析角色言行是否与性格设定不符
        - 严重程度：轻微/明显/严重
        - 返回高亮标注 + 修改建议
        """
        issues: list[ReviewIssue] = []

        # 构建 OOC 检测 prompt
        char_name = character.get('name', '未知角色')
        char_personality = character.get('personality', '')
        char_background = character.get('background', '')
        char_gender = character.get('gender', '')
        char_age = character.get('age', '')

        if not char_personality and not char_background:
            # 没有角色设定，无法检测
            return issues

        prompt = f"""你是一个角色一致性审查专家。请分析以下内容，检查角色是否存在OOC（Out Of Character）问题。

角色信息：
- 姓名：{char_name}
- 性别：{char_gender or '未设定'}
- 年龄：{char_age or '未设定'}
- 性格：{char_personality}
- 背景：{char_background}

待检测内容：
{content}

请分析角色言行是否符合其性格设定。如果存在OOC问题，请以JSON格式返回：

{{
    "has_ooc": true/false,
    "issues": [
        {{
            "severity": "low/medium/high",
            "location": "具体位置或段落",
            "description": "问题描述",
            "suggestion": "修改建议"
        }}
    ]
}}

只返回JSON，不要有其他内容。"""

        try:
            response = await self.llm.generate(prompt)
            
            # 解析 JSON 响应
            import json
            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                if result.get('has_ooc', False):
                    for issue in result.get('issues', []):
                        issues.append(ReviewIssue(
                            type='ooc',
                            severity=issue.get('severity', 'medium'),
                            location=issue.get('location', '未知'),
                            description=issue.get('description', ''),
                            suggestion=issue.get('suggestion', '')
                        ))
        except Exception as e:
            # LLM 调用失败时记录日志但不阻断流程
            print(f"OOC检测失败: {str(e)}")

        return issues

    def check_sensitive_words(
        self,
        content: str,
        custom_words: list[str] = None,
    ) -> list[ReviewIssue]:
        """敏感词/合规检测：
        - 内置涉政/涉黄/涉暴词库
        - 自定义敏感词（分级警告）
        - 返回：提示/警告/高危
        """
        issues: list[ReviewIssue] = []
        sensitive_words = self._load_sensitive_words()

        # 检测涉政词汇
        political_words = sensitive_words.get('political', [])
        for word in political_words:
            if word in content:
                issues.append(ReviewIssue(
                    type='sensitive',
                    severity='high',
                    location=f"包含敏感词: '{word}'",
                    description=f"检测到涉政敏感词: '{word}'",
                    suggestion=f"建议删除或替换词汇 '{word}'"
                ))

        # 检测涉黄词汇
        adult_words = sensitive_words.get('adult', [])
        for word in adult_words:
            if word in content:
                issues.append(ReviewIssue(
                    type='sensitive',
                    severity='high',
                    location=f"包含敏感词: '{word}'",
                    description=f"检测到涉黄敏感词: '{word}'",
                    suggestion=f"建议删除或替换词汇 '{word}'"
                ))

        # 检测涉暴词汇
        violence_words = sensitive_words.get('violence', [])
        for word in violence_words:
            if word in content:
                issues.append(ReviewIssue(
                    type='sensitive',
                    severity='high',
                    location=f"包含敏感词: '{word}'",
                    description=f"检测到涉暴敏感词: '{word}'",
                    suggestion=f"建议删除或替换词汇 '{word}'"
                ))

        # 检测自定义敏感词
        if custom_words:
            for word in custom_words:
                if word in content:
                    issues.append(ReviewIssue(
                        type='sensitive',
                        severity='medium',
                        location=f"包含自定义敏感词: '{word}'",
                        description=f"检测到自定义敏感词: '{word}'",
                        suggestion=f"建议删除或替换词汇 '{word}'"
                    ))

        return issues

    def _calculate_score(self, issues: list[ReviewIssue]) -> float:
        """根据问题计算综合评分（0-10分）"""
        if not issues:
            return 10.0  # 无问题满分

        # 扣分规则
        deductions = {
            'high': 2.0,
            'medium': 1.0,
            'low': 0.5,
        }

        total_deduction = 0.0
        for issue in issues:
            deduction = deductions.get(issue['severity'], 1.0)
            total_deduction += deduction

        # 最低0分，最高10分
        score = max(0.0, min(10.0, 10.0 - total_deduction))
        return round(score, 1)


def get_review_service() -> ReviewService:
    """获取审查服务实例（每次创建新实例避免状态问题）"""
    return ReviewService()
