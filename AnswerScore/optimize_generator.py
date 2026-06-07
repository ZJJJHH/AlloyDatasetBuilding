#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化答案生成器 - 综合三个大模型的答案，生成最优答案
"""

import json
import os
import sys
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPTIMIZE_PROMPT_TEMPLATE
from score_client import ScoreClient


class OptimizeGenerator:
    """优化答案生成器"""
    
    def __init__(self, score_model_client: ScoreClient):
        self.client = score_model_client
    
    def optimize_answer(self, question: Dict[str, Any], question_type: str,
                       score_details: Dict[str, Dict[str, str]]) -> Optional[str]:
        """优化答案"""
        try:
            question_text = question.get('question_text', '')
            scenario_info = json.dumps(question.get(f'{question_type}_scenario', {}), ensure_ascii=False, indent=2)
            
            answer_a = question.get('answer_deepseek', {}).get('content', '')
            answer_b = question.get('answer_qwen', {}).get('content', '')
            answer_c = question.get('answer_minimax', {}).get('content', '')
            
            score_details_text = self._format_score_details(score_details)
            
            prompt = OPTIMIZE_PROMPT_TEMPLATE.format(
                question_text=question_text,
                scenario_info=scenario_info,
                answer_a=answer_a,
                answer_b=answer_b,
                answer_c=answer_c,
                score_details=score_details_text
            )
            
            optimized_text = self.client.generate_text(prompt)
            
            return optimized_text
        
        except Exception as e:
            print(f"答案优化失败: {str(e)}")
            return None
    
    def _format_score_details(self, score_details: Dict[str, Dict[str, str]]) -> str:
        """格式化评分详情"""
        text = ""
        
        answer_labels = {
            'answer_a': 'DeepSeek',
            'answer_b': 'Qwen',
            'answer_c': 'MiniMax'
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
    
    def update_question_with_optimized_answer(self, question: Dict[str, Any], 
                                               optimized_answer: str,
                                               question_type: str) -> Dict[str, Any]:
        """用优化后的答案更新问题"""
        original_question_type = question.get('question_type', question_type)
        
        optimized_entry = {
            'content': optimized_answer,
            'data_sources': question.get(f'answer_{self._get_best_model(question)}', {}).get('data_sources', []),
            'model_used': f"{self.client.model_name}_optimized"
        }
        
        question[f'answer_{self.client.model_name}_optimized'] = optimized_entry
        
        return question
    
    def _get_best_model(self, question: Dict[str, Any]) -> str:
        """获取最佳模型"""
        models = ['deepseek', 'qwen', 'minimax']
        best_model = 'qwen'
        max_score = -1
        
        for model in models:
            answer_key = f'answer_{model}'
            if answer_key in question and 'score' in question[answer_key]:
                total_score = question[answer_key]['score'].get('总分', '0/100')
                try:
                    score = int(total_score.split('/')[0])
                    if score > max_score:
                        max_score = score
                        best_model = model
                except:
                    continue
        
        return best_model


if __name__ == "__main__":
    print("优化生成器初始化测试")
    
    client = ScoreClient()
    generator = OptimizeGenerator(client)
    
    print(f"优化模型: {client.model_name}")
    print("优化生成器初始化完成")
