#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描全0评分数据脚本
查找所有答案的评分字段中存在全0的情况
"""

import json
import argparse
import os
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='扫描全0评分数据')
    parser.add_argument('--input_json', type=str, required=True,
                        help='输入JSON文件路径（后处理前的数据格式）')
    
    return parser.parse_args()


def check_answer_scores(answer_data, answer_field):
    """
    检查答案的评分是否全为0
    
    Args:
        answer_data: 答案数据
        answer_field: 答案字段名
        
    Returns:
        dict: 检查结果
    """
    results = {
        'answer_field': answer_field,
        'has_zero_score': False,
        'zero_scores': [],
        'score_fields': ['score', 'score2-1', 'score2-2']
    }
    
    for score_field in results['score_fields']:
        if score_field in answer_data:
            score_data = answer_data[score_field]
            if isinstance(score_data, dict):
                # 检查总分是否为0
                if '总分' in score_data:
                    total_score = score_data['总分']
                    if isinstance(total_score, str) and '/' in total_score:
                        try:
                            score_val = int(total_score.split('/')[0])
                            if score_val == 0:
                                results['has_zero_score'] = True
                                results['zero_scores'].append({
                                    'field': score_field,
                                    'total': total_score,
                                    'dimensions': {}
                                })
                                # 记录各维度评分
                                for dim, dim_score in score_data.items():
                                    if dim not in ['总分', 'score_model'] and isinstance(dim_score, str) and '/' in dim_score:
                                        try:
                                            dim_val = int(dim_score.split('/')[0])
                                            if dim_val == 0:
                                                results['zero_scores'][-1]['dimensions'][dim] = dim_score
                                        except (ValueError, IndexError):
                                            continue
                        except (ValueError, IndexError):
                            continue
                    elif isinstance(total_score, (int, float)) and total_score == 0:
                        results['has_zero_score'] = True
                        results['zero_scores'].append({
                            'field': score_field,
                            'total': total_score,
                            'dimensions': {}
                        })
    
    return results


def scan_questions(data):
    """
    扫描所有问题中的全0评分
    
    Args:
        data: JSON数据
        
    Returns:
        list: 全0评分问题列表
    """
    questions = data.get('questions', [])
    zero_score_questions = []
    
    for question in questions:
        question_id = question.get('question_id', '')
        question_text = question.get('question_text', '')
        
        # 遍历所有答案字段
        answer_fields = ['answer_deepseek', 'answer_qwen', 'answer_minimax', 'answer_glm-5_optimized']
        
        for answer_field in answer_fields:
            if answer_field not in question:
                continue
            
            answer_data = question[answer_field]
            if not isinstance(answer_data, dict):
                continue
            
            # 检查评分
            check_result = check_answer_scores(answer_data, answer_field)
            
            if check_result['has_zero_score']:
                answer_content = answer_data.get('content', '')
                zero_score_questions.append({
                    'question_id': question_id,
                    'question_text': question_text[:100] + '...' if len(question_text) > 100 else question_text,
                    'answer_field': answer_field,
                    'model_used': answer_data.get('model_used', 'unknown'),
                    'answer_content': answer_content,
                    'zero_scores': check_result['zero_scores']
                })
    
    return zero_score_questions


def print_results(zero_score_questions, output_path):
    """
    打印扫描结果
    
    Args:
        zero_score_questions: 全0评分问题列表
        output_path: 输入文件路径
    """
    print(f"\n{'='*80}")
    print(f"全0评分数据扫描结果")
    print(f"{'='*80}")
    print(f"输入文件: {output_path}")
    print(f"{'='*80}\n")
    
    if not zero_score_questions:
        print("✓ 未发现全0评分的数据")
        return
    
    print(f"发现 {len(zero_score_questions)} 个存在全0评分的问题:\n")
    
    for idx, item in enumerate(zero_score_questions, 1):
        print(f"{'-'*80}")
        print(f"问题 {idx}:")
        print(f"{'-'*80}")
        print(f"问题ID: {item['question_id']}")
        print(f"问题文本: {item['question_text']}")
        print(f"答案字段: {item['answer_field']}")
        print(f"生成模型: {item['model_used']}")
        print(f"答案内容:")
        print(f"{item['answer_content']}")
        print(f"全0评分详情:")
        
        for score_info in item['zero_scores']:
            print(f"  - 评分字段: {score_info['field']}")
            print(f"    总分: {score_info['total']}")
            
            if score_info['dimensions']:
                print(f"    全0维度:")
                for dim, dim_score in score_info['dimensions'].items():
                    print(f"      * {dim}: {dim_score}")
        
        print()


def main():
    """主函数"""
    args = parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.input_json):
        print(f"错误：文件不存在 - {args.input_json}")
        return
    
    print(f"\n{'='*80}")
    print(f"全0评分数据扫描")
    print(f"{'='*80}")
    print(f"输入文件: {args.input_json}")
    
    # 加载数据
    print(f"\n正在加载数据...")
    with open(args.input_json, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    total_questions = data.get('metadata', {}).get('total_questions', 0)
    print(f"总问题数: {total_questions}")
    
    # 扫描数据
    print(f"\n正在扫描全0评分数据...")
    zero_score_questions = scan_questions(data)
    
    # 打印结果
    print_results(zero_score_questions, args.input_json)
    
    # 统计信息
    print(f"{'='*80}")
    print(f"统计信息")
    print(f"{'='*80}")
    print(f"总问题数: {total_questions}")
    print(f"存在全0评分的问题数: {len(zero_score_questions)}")
    print(f"全0评分比例: {len(zero_score_questions)/total_questions*100:.2f}%")
    print()


if __name__ == "__main__":
    main()
