# ==================== 第二轮评分配置 ====================
# 评分轮次标识（用于生成score2-x字段名）
SCORE_ROUND = '2-2'

# 选择使用的评分大模型：'kimi'、'deepseek'、'qwen'、'glm' 或 'minimax'
SCORE_MODEL = 'deepseek'

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<qwen-api-endpoint>",
    "model": "deepseek-r1",
    "max_tokens": 5000,
    "temperature": 0.5,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# Qwen API配置
QWEN_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<qwen-api-endpoint>",
    "model": "qwen3.5-397b-a17b",
    "max_tokens": 2000,
    "temperature": 0.7,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# GLM API配置
GLM_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": '<qwen-api-endpoint>',
    "model": "glm-5",
    "max_tokens": 2000,
    "temperature": 1.0,
    "retry_count": 3,
    "delay_between_calls": 2.0
}

# MiniMax API配置
MINIMAX_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<qwen-api-endpoint>",
    "model": "MiniMax-M2.5",
    "max_tokens": 2000,
    "temperature": 0.7,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# Kimi API配置（第二轮评分专用）
KIMI_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<qwen-api-endpoint>",
    "model": "kimi-k2.5",
    "max_tokens": 5000,
    "temperature": 0.5,
    "retry_count": 3,
    "delay_between_calls": 1.5
}

# ==================== 评分维度配置 ====================
# 每个问题类型有不同的评分维度和权重（与第一轮评分保持一致）

# What_if 问题评分配置（反事实问）
WHAT_IF_SCORE_CONFIG = {
    "dimensions": {
        "方案可行性": {"weight": 30, "description": "方案是否切实可行，工艺是否可实现"},
        "技术合理性": {"weight": 30, "description": "技术路线是否合理，机理是否科学"},
        "数据支持度": {"weight": 20, "description": "是否有数据源支持，引用是否准确"},
        "方案多样性": {"weight": 10, "description": "是否提供多个方案，方案是否多样"},
        "表达清晰度": {"weight": 10, "description": "表达是否清晰，结构是否合理"}
    },
    "total_score": 100
}

# Causal 问题评分配置（因果问）
CAUSAL_SCORE_CONFIG = {
    "dimensions": {
        "因果关系正确性": {"weight": 30, "description": "因果关系是否正确"},
        "机理解释深度": {"weight": 30, "description": "是否深入解释机理"},
        "专业术语使用": {"weight": 20, "description": "是否使用专业术语"},
        "逻辑连贯性": {"weight": 20, "description": "推理过程是否连贯"}
    },
    "total_score": 100
}

# Mitigation 问题评分配置（失效诊断问）
MITIGATION_SCORE_CONFIG = {
    "dimensions": {
        "问题诊断准确性": {"weight": 30, "description": "问题诊断是否准确"},
        "解决方案可行性": {"weight": 30, "description": "解决方案是否切实可行"},
        "系统性": {"weight": 20, "description": "是否系统性分析问题"},
        "可操作性": {"weight": 20, "description": "解决方案是否可操作"}
    },
    "total_score": 100
}

# Pathway 问题评分配置（机制问）
PATHWAY_SCORE_CONFIG = {
    "dimensions": {
        "路径完整性": {"weight": 30, "description": "路径描述是否完整"},
        "机理清晰度": {"weight": 30, "description": "机理描述是否清晰"},
        "逻辑连贯性": {"weight": 20, "description": "推理过程是否连贯"},
        "专业深度": {"weight": 20, "description": "专业深度是否足够"}
    },
    "total_score": 100
}

# ==================== 评分提示词配置 ====================
SCORE_PROMPT_TEMPLATES = {
    "what_if": """你是一个专业的材料科学专家，需要评估钛合金反事实问（What-if）的答案质量。

问题：
{question_text}

场景信息：
{scenario_info}

答案A：
{answer_a}

答案B：
{answer_b}

答案C：
{answer_c}

答案D：
{answer_d}

请从以下维度对每个答案进行评分。注意：每个维度的评分必须严格遵守其最大分值，不能超过：

1. 方案可行性（30分）：方案是否切实可行，工艺是否可实现，满分30分
2. 技术合理性（30分）：技术路线是否合理，机理是否科学，满分30分
3. 数据支持度（20分）：是否有数据源支持，引用是否准确，满分20分
4. 方案多样性（10分）：是否提供多个方案，方案是否多样，满分10分
5. 表达清晰度（10分）：表达是否清晰，结构是否合理，满分10分

请严格按照以下格式输出，每个维度的分数不能超过其最大值：
【答案A评分】
方案可行性: X/30
技术合理性: X/30
数据支持度: X/20
方案多样性: X/10
表达清晰度: X/10
总分：XX/100

【答案B评分】
方案可行性: X/30
技术合理性: X/30
数据支持度: X/20
方案多样性: X/10
表达清晰度: X/10
总分：XX/100

【答案C评分】
方案可行性: X/30
技术合理性: X/30
数据支持度: X/20
方案多样性: X/10
表达清晰度: X/10
总分：XX/100

【答案D评分】
方案可行性: X/30
技术合理性: X/30
数据支持度: X/20
方案多样性: X/10
表达清晰度: X/10
总分：XX/100
""",
    
    "causal": """你是一个专业的材料科学专家，需要评估钛合金因果问（Causal）的答案质量。

问题：
{question_text}

场景信息：
{scenario_info}

答案A：
{answer_a}

答案B：
{answer_b}

答案C：
{answer_c}

答案D：
{answer_d}

请从以下维度对每个答案进行评分。注意：每个维度的评分必须严格遵守其最大分值，不能超过：

1. 因果关系正确性（30分）：因果关系是否正确，满分30分
2. 机理解释深度（30分）：是否深入解释机理，满分30分
3. 专业术语使用（20分）：是否使用专业术语，满分20分
4. 逻辑连贯性（20分）：推理过程是否连贯，满分20分

请严格按照以下格式输出，每个维度的分数不能超过其最大值：
【答案A评分】
因果关系正确性: X/30
机理解释深度: X/30
专业术语使用: X/20
逻辑连贯性: X/20
总分：XX/100

【答案B评分】
因果关系正确性: X/30
机理解释深度: X/30
专业术语使用: X/20
逻辑连贯性: X/20
总分：XX/100

【答案C评分】
因果关系正确性: X/30
机理解释深度: X/30
专业术语使用: X/20
逻辑连贯性: X/20
总分：XX/100

【答案D评分】
因果关系正确性: X/30
机理解释深度: X/30
专业术语使用: X/20
逻辑连贯性: X/20
总分：XX/100
""",
    
    "mitigation": """你是一个专业的材料科学专家，需要评估钛合金失效诊断问（Mitigation）的答案质量。

问题：
{question_text}

场景信息：
{scenario_info}

答案A：
{answer_a}

答案B：
{answer_b}

答案C：
{answer_c}

答案D：
{answer_d}

请从以下维度对每个答案进行评分。注意：每个维度的评分必须严格遵守其最大分值，不能超过：

1. 问题诊断准确性（30分）：问题诊断是否准确，满分30分
2. 解决方案可行性（30分）：解决方案是否切实可行，满分30分
3. 系统性（20分）：是否系统性分析问题，满分20分
4. 可操作性（20分）：解决方案是否可操作，满分20分

请严格按照以下格式输出，每个维度的分数不能超过其最大值：
【答案A评分】
问题诊断准确性: X/30
解决方案可行性: X/30
系统性: X/20
可操作性: X/20
总分：XX/100

【答案B评分】
问题诊断准确性: X/30
解决方案可行性: X/30
系统性: X/20
可操作性: X/20
总分：XX/100

【答案C评分】
问题诊断准确性: X/30
解决方案可行性: X/30
系统性: X/20
可操作性: X/20
总分：XX/100

【答案D评分】
问题诊断准确性: X/30
解决方案可行性: X/30
系统性: X/20
可操作性: X/20
总分：XX/100
""",
    
    "pathway": """你是一个专业的材料科学专家，需要评估钛合金机制问（Pathway）的答案质量。

问题：
{question_text}

场景信息：
{scenario_info}

答案A：
{answer_a}

答案B：
{answer_b}

答案C：
{answer_c}

答案D：
{answer_d}

请从以下维度对每个答案进行评分。注意：每个维度的评分必须严格遵守其最大分值，不能超过：

1. 路径完整性（30分）：路径描述是否完整，满分30分
2. 机理清晰度（30分）：机理描述是否清晰，满分30分
3. 逻辑连贯性（20分）：推理过程是否连贯，满分20分
4. 专业深度（20分）：专业深度是否足够，满分20分

请严格按照以下格式输出，每个维度的分数不能超过其最大值：
【答案A评分】
路径完整性: X/30
机理清晰度: X/30
逻辑连贯性: X/20
专业深度: X/20
总分：XX/100

【答案B评分】
路径完整性: X/30
机理清晰度: X/30
逻辑连贯性: X/20
专业深度: X/20
总分：XX/100

【答案C评分】
路径完整性: X/30
机理清晰度: X/30
逻辑连贯性: X/20
专业深度: X/20
总分：XX/100

【答案D评分】
路径完整性: X/30
机理清晰度: X/30
逻辑连贯性: X/20
专业深度: X/20
总分：XX/100
"""
}


