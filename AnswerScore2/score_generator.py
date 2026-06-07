#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二轮答案评分器 - 为四个大模型生成的答案进行评分
支持五个维度的问题类型，每个维度有不同的评分方案
"""

import json
import os
import sys
import re
from typing import Dict, Any, Optional, List
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import (
    WHAT_IF_SCORE_CONFIG, CAUSAL_SCORE_CONFIG,
    MITIGATION_SCORE_CONFIG, PATHWAY_SCORE_CONFIG, SCORE_PROMPT_TEMPLATES,
    SCORE_ROUND
)
from score_client import ScoreClient
from score_rag_retriever import ScoreRAGRetriever


class ScoreGenerator:
    """第二轮答案评分器"""
    
    def __init__(self, score_model_client: ScoreClient, data_source_path: str = '/path/to/AlloyDatasetBuilding/Ti_data.jsonl'):
        self.client = score_model_client
        self.retriever = ScoreRAGRetriever(data_source_path)
        self.score_configs = {
            'what_if': WHAT_IF_SCORE_CONFIG,
            'causal': CAUSAL_SCORE_CONFIG,
            'mitigation': MITIGATION_SCORE_CONFIG,
            'pathway': PATHWAY_SCORE_CONFIG
        }
        self.prompt_templates = SCORE_PROMPT_TEMPLATES
        self.score_round = SCORE_ROUND
    
    def extract_score_details(self, score_text: str) -> Dict[str, Dict[str, str]]:
        """从评分文本中提取评分详情"""
        scores = {}
        
        patterns = [
            r'【答案\s*A\s*评分】(.*?)【答案\s*B\s*评分】',
            r'【答案\s*B\s*评分】(.*?)【答案\s*C\s*评分】',
            r'【答案\s*C\s*评分】(.*?)【答案\s*D\s*评分】',
            r'【答案\s*D\s*评分】(.*)'
        ]
        
        answer_labels = ['answer_a', 'answer_b', 'answer_c', 'answer_d']
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, score_text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                scores[answer_labels[i]] = self._parse_single_answer_scores(content)
        
        return scores
    
    def _parse_single_answer_scores(self, content: str) -> Dict[str, str]:
        """解析单个答案的评分"""
        scores = {}
        
        lines = content.split('\n')
        current_dimension = None
        
        for line in lines:
            line = line.strip()
            
            # 尝试匹配带序号的评分行（如 "1. 方案可行性: X/30"）
            match = re.match(r'^[一一二三四五1-5]\s*[、.]\s*(.+?)\s*[:：]\s*(\d+)/(\d+)', line)
            if match:
                dimension = match.group(1).strip()
                score = match.group(2).strip()
                scores[dimension] = f"{score}/{match.group(3).strip()}"
                current_dimension = dimension
                continue
            
            # 尝试匹配不带序号的评分行（如 "方案可行性: X/30"）
            match = re.match(r'^(.+?)\s*[:：]\s*(\d+)/(\d+)', line)
            if match:
                dimension = match.group(1).strip()
                score = match.group(2).strip()
                scores[dimension] = f"{score}/{match.group(3).strip()}"
                current_dimension = dimension
                continue
            
            # 尝试匹配带方括号的评分行（如 "[方案可行性]: X/30"）
            match = re.match(r'^\[?(.+?)\]?\s*[:：]\s*(\d+)/(\d+)', line)
            if match:
                dimension = match.group(1).strip()
                score = match.group(2).strip()
                scores[dimension] = f"{score}/{match.group(3).strip()}"
                current_dimension = dimension
                continue
            
            elif current_dimension and line.startswith('理由：'):
                scores[f"{current_dimension}_reason"] = line[3:].strip()
        
        return scores
    
    def calculate_total_score(self, scores: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """计算总分"""
        total_scores = {}
        
        for answer_key, answer_scores in scores.items():
            total = 0
            max_total = 0
            
            for dimension, score_str in answer_scores.items():
                # 跳过 '总分' 维度和包含 '_reason' 的维度
                if dimension == '总分' or '_reason' in dimension or '/' not in score_str:
                    continue
                    
                score, max_score = score_str.split('/')
                try:
                    total += int(score)
                    max_total += int(max_score)
                except ValueError:
                    continue
            
            total_scores[answer_key] = f"{total}/{max_total}"
        
        return total_scores
    
    def generate_score_prompt(self, question: Dict[str, Any], question_type: str) -> str:
        """生成评分提示词"""
        template = self.prompt_templates.get(question_type, self.prompt_templates['what_if'])
        
        question_text = question.get('question_text', '')
        scenario_info = json.dumps(question.get(f'{question_type}_scenario', {}), ensure_ascii=False, indent=2)
        
        answer_a = question.get('answer_deepseek', {}).get('content', '')
        answer_b = question.get('answer_qwen', {}).get('content', '')
        answer_c = question.get('answer_minimax', {}).get('content', '')
        answer_d = question.get(f'answer_glm-5_optimized', {}).get('content', '')
        
        # 获取数据源信息
        data_sources_text = self._get_data_sources_info(question, question_type)
        
        prompt = template.format(
            question_text=question_text,
            scenario_info=scenario_info,
            answer_a=answer_a,
            answer_b=answer_b,
            answer_c=answer_c,
            answer_d=answer_d,
            data_sources_info=data_sources_text
        )
        
        return prompt
    
    def _format_score_details(self, score_details: Dict[str, Dict[str, str]]) -> str:
        """格式化评分详情"""
        text = ""
        
        answer_labels = {
            'answer_a': 'DeepSeek',
            'answer_b': 'Qwen',
            'answer_c': 'MiniMax',
            'answer_d': 'GLM-5优化'
        }
        
        for answer_key, scores in score_details.items():
            label = answer_labels.get(answer_key, answer_key)
            text += f"【{label}答案评分详情】\n"
            
            for dimension, value in scores.items():
                if not dimension.endswith('_reason'):
                    reason = scores.get(f"{dimension}_reason", "无")
                    text += f"{dimension}: {value}\n"
                    text += f"理由：{reason}\n\n"
            
            text += "\n"
        
        return text
    
    def score_question(self, question: Dict[str, Any], question_type: str) -> Optional[Dict[str, Any]]:
        """为单个问题评分"""
        try:
            prompt = self.generate_score_prompt(question, question_type)
            
            score_text = self.client.generate_text(prompt)
            
            if not score_text:
                print("评分生成失败")
                return None
            
            score_details = self.extract_score_details(score_text)
            total_scores = self.calculate_total_score(score_details)
            
            return {
                'score_details': score_details,
                'total_scores': total_scores,
                'raw_score_text': score_text
            }
        
        except Exception as e:
            print(f"评分失败: {str(e)}")
            return None
    
    def add_scores_to_question(self, question: Dict[str, Any], 
                               score_result: Dict[str, Any],
                               question_type: str) -> Dict[str, Any]:
        """将评分添加到问题中，使用score2-x格式的字段名"""
        score_details = score_result['score_details']
        total_scores = score_result['total_scores']
        
        answer_mappings = {
            'answer_a': 'answer_deepseek',
            'answer_b': 'answer_qwen',
            'answer_c': 'answer_minimax',
            'answer_d': f'answer_glm-5_optimized'
        }
        
        score_config = self.score_configs.get(question_type, PATHWAY_SCORE_CONFIG)
        expected_dimensions = list(score_config.get('dimensions', {}).keys())
        
        for answer_key, score_data in score_details.items():
            original_key = answer_mappings.get(answer_key, answer_key)
            
            if original_key in question:
                score_entry = {}
                for dimension, value in score_data.items():
                    if not dimension.endswith('_reason'):
                        score_entry[dimension] = value
                
                for dimension in expected_dimensions:
                    if dimension not in score_entry:
                        score_entry[dimension] = "0/0"
                
                score_entry['总分'] = total_scores.get(answer_key, "0/100")
                score_entry['score_model'] = self.client.model_name
                
                # 使用score2-x格式的字段名
                question[original_key][f'score{self.score_round}'] = score_entry
        
        return question
    
    def _get_data_sources_info(self, question: Dict[str, Any], question_type: str) -> str:
        """
        获取问题对应的数据源信息（使用RAG检索器）
        
        Args:
            question: 问题字典
            question_type: 问题类型
        
        Returns:
            格式化后的数据源信息文本
        """
        # 从问题场景中提取信息进行检索
        scenario = question.get(f'{question_type}_scenario', {})
        
        # 如果有场景信息，使用RAG检索器获取相关数据
        if scenario:
            return self.retriever.retrieve_and_format(scenario, k=3)
        
        return "未找到相关数据源信息"


if __name__ == "__main__":
    print("第二轮评分器初始化测试")
    
    client = ScoreClient()
    generator = ScoreGenerator(client)
    
    print(f"评分模型: {client.model_name}")
    print(f"评分轮次: {generator.score_round}")
    print("第二轮评分器初始化完成")
