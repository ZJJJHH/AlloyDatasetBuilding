#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据后处理脚本
- 重命名JSON文件（去掉_questions后缀）
- 保留指定字段
- 对答案按总分排序并重命名
- 重命名评分字段
"""

import json
import argparse
import os
import re
from pathlib import Path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='数据后处理脚本')
    parser.add_argument('--input_json', type=str, required=True,
                        help='输入JSON文件路径')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='输出目录（默认为输入文件所在目录）')
    
    return parser.parse_args()


def extract_metadata_info(question_data):
    """
    提取metadata中的model_used和causal_complexity信息
    
    Args:
        question_data: 原始问题数据
        
    Returns:
        dict: 提取的metadata信息
    """
    metadata = question_data.get('metadata', {})
    
    extracted = {}
    
    if 'model_used' in metadata:
        extracted['model_used'] = metadata['model_used']
    
    if 'causal_complexity' in metadata:
        extracted['causal_complexity'] = metadata['causal_complexity']
    
    return extracted


def extract_answer_info(answer_data):
    """
    提取答案中的必要信息
    
    Args:
        answer_data: 原始答案数据
        
    Returns:
        dict: 提取的答案信息
    """
    extracted = {}
    
    if 'content' in answer_data:
        extracted['content'] = answer_data['content']
    
    if 'model_used' in answer_data:
        extracted['model_used'] = answer_data['model_used']
    
    if 'score2-1' in answer_data:
        extracted['score_1'] = answer_data['score2-1']
    
    if 'score2-2' in answer_data:
        extracted['score_2'] = answer_data['score2-2']
    
    return extracted


def calculate_total_score(answer_data):
    """
    计算答案的总分（score2-1和score2-2的总分之和）
    
    Args:
        answer_data: 答案数据
        
    Returns:
        float: 总分
    """
    total_score = 0
    
    for score_key in ['score2-1', 'score2-2']:
        if score_key in answer_data:
            score_data = answer_data[score_key]
            if '总分' in score_data:
                total_score_str = score_data['总分']
                if isinstance(total_score_str, str) and '/' in total_score_str:
                    try:
                        score_val = int(total_score_str.split('/')[0])
                        total_score += score_val
                    except (ValueError, IndexError):
                        continue
                elif isinstance(total_score_str, (int, float)):
                    total_score += float(total_score_str)
    
    return total_score


def process_question(question_data):
    """
    处理单个问题数据
    
    Args:
        question_data: 原始问题数据
        
    Returns:
        dict: 处理后的问题数据
    """
    processed = {}
    
    # 保留question_id
    if 'question_id' in question_data:
        processed['question_id'] = question_data['question_id']
    
    # 保留question_type
    if 'question_type' in question_data:
        processed['question_type'] = question_data['question_type']
    
    # 保留question_text
    if 'question_text' in question_data:
        processed['question_text'] = question_data['question_text']
    
    # 提取metadata信息
    processed['metadata'] = extract_metadata_info(question_data)
    
    # 收集所有答案
    answers = []
    answer_fields = ['answer_deepseek', 'answer_qwen', 'answer_minimax', 'answer_glm-5_optimized']
    
    for answer_field in answer_fields:
        if answer_field in question_data:
            answer_data = question_data[answer_field]
            if isinstance(answer_data, dict):
                # 计算总分
                total_score = calculate_total_score(answer_data)
                # 提取答案信息
                extracted_answer = extract_answer_info(answer_data)
                extracted_answer['total_score'] = total_score
                answers.append(extracted_answer)
    
    # 按总分从大到小排序
    answers.sort(key=lambda x: x['total_score'], reverse=True)
    
    # 重命名答案字段
    answer_names = ['answer_A', 'answer_B', 'answer_C', 'answer_D']
    processed['answers'] = []
    
    for i, answer in enumerate(answers):
        answer_name = answer_names[i] if i < len(answer_names) else f'answer_{i}'
        
        # 移除total_score字段
        answer_without_score = {k: v for k, v in answer.items() if k != 'total_score'}
        processed['answers'].append({
            answer_name: answer_without_score
        })
    
    return processed


def process_dataset(data):
    """
    处理整个数据集
    
    Args:
        data: 原始数据
        
    Returns:
        dict: 处理后的数据
    """
    processed_data = {}
    
    # 保留metadata信息
    if 'metadata' in data:
        processed_data['metadata'] = data['metadata'].copy()
        # 更新question_type（去掉_questions后缀）
        if 'question_type' in processed_data['metadata']:
            question_type = processed_data['metadata']['question_type']
            if question_type.endswith('_questions'):
                question_type = question_type[:-10]  # 去掉'_questions'
                processed_data['metadata']['question_type'] = question_type
    
    # 处理所有问题
    questions = data.get('questions', [])
    processed_questions = []
    
    for question in questions:
        processed_question = process_question(question)
        processed_questions.append(processed_question)
    
    processed_data['questions'] = processed_questions
    
    return processed_data


def generate_output_filename(input_path):
    """
    生成输出文件名（去掉_questions后缀）
    
    Args:
        input_path: 输入文件路径
        
    Returns:
        str: 输出文件路径
    """
    input_path = Path(input_path)
    
    # 获取文件名（不含扩展名）
    filename = input_path.stem
    
    # 去掉_questions后缀
    if filename.endswith('_questions'):
        filename = filename[:-10]
    
    # 生成新文件名
    output_filename = filename + input_path.suffix
    
    return output_filename


def main():
    """主函数"""
    args = parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.input_json):
        print(f"错误：文件不存在 - {args.input_json}")
        return
    
    # 设置输出目录
    if args.output_dir is None:
        output_dir = os.path.dirname(args.input_json)
    else:
        output_dir = args.output_dir
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"数据后处理")
    print(f"{'='*60}")
    print(f"输入文件: {args.input_json}")
    print(f"输出目录: {output_dir}")
    
    # 加载数据
    print(f"\n正在加载数据...")
    with open(args.input_json, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    total_questions = data.get('metadata', {}).get('total_questions', 0)
    print(f"总问题数: {total_questions}")
    
    # 处理数据
    print(f"\n正在处理数据...")
    processed_data = process_dataset(data)
    
    # 生成输出文件名
    output_filename = generate_output_filename(args.input_json)
    output_path = os.path.join(output_dir, output_filename)
    
    # 保存处理后的数据
    print(f"\n正在保存数据...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 保存处理后的数据: {output_path}")
    
    # 输出统计信息
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"{'='*60}")
    
    # 统计信息
    questions = processed_data.get('questions', [])
    if questions:
        # 统计每个问题的答案数量
        answer_counts = [len(q.get('answers', [])) for q in questions]
        avg_answers = sum(answer_counts) / len(answer_counts) if answer_counts else 0
        
        print(f"\n处理后数据统计：")
        print(f"  - 问题数量: {len(questions)}")
        print(f"  - 平均每个问题的答案数: {avg_answers:.2f}")
        
        # 检查metadata字段
        if questions:
            first_question = questions[0]
            print(f"\n  - 保留的字段:")
            print(f"    - question_id")
            print(f"    - question_type")
            print(f"    - question_text")
            print(f"    - metadata (包含 model_used, causal_complexity)")
            print(f"    - answers (包含 answer_A, answer_B, answer_C, answer_D)")
            print(f"      - content")
            print(f"      - model_used")
            print(f"      - score_1 (原 score2-1)")
            print(f"      - score_2 (原 score2-2)")
    
    print()


if __name__ == "__main__":
    main()
