#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 答案生成系统配置
所有大模型API密钥和参数均可在此处硬编码修改
"""

# ==================== 大模型配置 ====================
# 选择使用的模型：'deepseek'、'qwen'、'glm' 或 'minimax'
LLM_MODEL = 'minimax'  # 可修改：'deepseek'、'qwen'、'glm' 或 'minimax'

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    "api_key": "YOUR_API_KEY",  # 替换为您的DeepSeek API密钥
    "base_url": "<deepseek-api-endpoint>",
    "model": "deepseek-chat",
    "max_tokens": 1500,
    "temperature": 1.0,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0  # API调用间隔（秒）
}

# Qwen API配置
QWEN_CONFIG = {
    "api_key": "YOUR_API_KEY",  # 替换为您的Qwen API密钥
    "base_url": "<qwen-api-endpoint>",
    "model": "qwen3.5-397b-a17b",
    "max_tokens": 1500,
    "temperature": 1.0,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# GLM API配置
GLM_CONFIG = {
    "api_key": "YOUR_API_KEY",  # 替换为您的GLM API密钥
    "base_url": '<glm-api-endpoint>',
    "model": "glm-4-7-251222",
    "max_tokens": 1500,
    "temperature": 1.0,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# MiniMax API配置
MINIMAX_CONFIG = {
    "api_key": "YOUR_API_KEY",  # 替换为您的MiniMax API密钥
    "base_url": "<qwen-api-endpoint>",
    "model": "MiniMax-M2.5",  # MiniMax模型名称
    "max_tokens": 1500,
    "temperature": 1.0,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# ==================== RAG检索配置 ====================
RAG_CONFIG = {
    "data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
    "retrieval_top_k": 10,  # 检索前K个最相关样本
    "retrieval_threshold": 0.3,  # 相似度阈值
    "enable_rag": True  # 是否启用RAG检索
}

# ==================== 数据路径配置 ====================
DATA_PATHS = {
    "what_if": "/path/to/AlloyDatasetBuilding/What_if/what_if_questions.json",
    "causal": "/path/to/AlloyDatasetBuilding/Causal/causal_questions.json",
    "mitigation": "/path/to/AlloyDatasetBuilding/Mitigation/mitigation_questions.json",
    "pathway": "/path/to/AlloyDatasetBuilding/Pathway/pathway_questions.json"
}

# ==================== 生成参数配置 ====================
GENERATION_CONFIG = {
    "batch_size": 1,  # 批处理大小（建议为1以避免API限流）
    "start_index": 0,  # 起始索引（用于断点续传）
    "end_index": None,  # 结束索引（None表示处理全部）
    "save_interval": 10,  # 保存间隔（每N条保存一次）
    "enable_backup": True  # 是否启用备份
}
