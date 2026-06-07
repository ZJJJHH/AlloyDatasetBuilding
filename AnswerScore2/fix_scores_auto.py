#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复第二轮评分错误脚本
先验证所有评分，然后自动重新评分有问题的样本
"""

import json
import subprocess
import sys
import os
from collections import defaultdict
from tqdm import tqdm

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from validate_scores import validate_scores_in_file, SCORE_CONFIGS

# 问题类型列表
QUESTION_TYPES = ['what_if', 'causal', 'mitigation', 'pathway']

# 评分器路径
SCORE_SINGLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'score_single_v2.py')


def get_invalid_questions(file_path, question_type):
    """
    获取有问题的评分信息
    
    Args:
        file_path: 文件路径
        question_type: 问题类型
        
    Returns:
        dict: 有问题的问题信息
    """
    print(f"\n{'='*60}")
    print(f"验证评分文件: {file_path}")
    print(f"{'='*60}\n")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    invalid_questions = defaultdict(list)
    missing_scores = defaultdict(list)
    
    answer_fields = ['answer_deepseek', 'answer_qwen', 'answer_minimax', 'answer_glm-5_optimized']
    
    for question in questions:
        question_id = question.get('question_id', '')
        has_errors = False
        
        for answer_field in answer_fields:
            if answer_field in question:
                answer = question[answer_field]
                if isinstance(answer, dict):
                    # 检查score2-2字段
                    if 'score2-2' in answer:
                        score2_1 = answer['score2-2']
                        if isinstance(score2_1, dict):
                            # 验证评分
                            errors = validate_score_entry(score2_1, question_type)
                            if errors:
                                has_errors = True
                                invalid_questions[question_id].append({
                                    'answer_field': answer_field,
                                    'errors': errors
                                })
                    elif 'score' in answer and isinstance(answer['score'], dict):
                        if 'score2-2' in answer['score']:
                            score2_1 = answer['score']['score2-2']
                            if isinstance(score2_1, dict):
                                errors = validate_score_entry(score2_1, question_type)
                                if errors:
                                    has_errors = True
                                    invalid_questions[question_id].append({
                                        'answer_field': answer_field,
                                        'errors': errors
                                    })
                    # 检查缺失的score2-2
                    else:
                        missing_scores[question_id].append(answer_field)
        
    return {
        'invalid_questions': dict(invalid_questions),
        'missing_scores': dict(missing_scores)
    }


def validate_score_entry(score_entry, question_type):
    """
    验证评分条目是否符合规范
    
    Args:
        score_entry: 评分条目字典
        question_type: 问题类型
        
    Returns:
        list: 错误信息列表
    """
    errors = []
    
    if not isinstance(score_entry, dict):
        errors.append("评分条目不是字典类型")
        return errors
    
    config = SCORE_CONFIGS.get(question_type)
    if not config:
        errors.append(f"未知的问题类型: {question_type}")
        return errors
    
    dimensions = config['dimensions']
    
    # 检查各维度评分是否超过最大值
    for dimension, max_score in dimensions.items():
        if dimension in score_entry:
            value = score_entry[dimension]
            if isinstance(value, str) and '/' in value:
                try:
                    score, max_s = value.split('/')
                    score_int = int(score)
                    max_s_int = int(max_s)
                    
                    if score_int > max_s_int:
                        errors.append(f"维度 '{dimension}' 评分 {score}/{max_s} 超过最大值 {max_s}")
                    
                    if max_s_int != max_score:
                        errors.append(f"维度 '{dimension}' 最大值不匹配: 期望 {max_score}, 实际 {max_s_int}")
                except ValueError:
                    errors.append(f"维度 '{dimension}' 评分格式错误: {value}")
    
    # 检查总分
    if '总分' in score_entry:
        total_value = score_entry['总分']
        if isinstance(total_value, str) and '/' in total_value:
            try:
                total_score, total_max = total_value.split('/')
                total_score_int = int(total_score)
                total_max_int = int(total_max)
                
                if total_score_int > total_max_int:
                    errors.append(f"总分 {total_value} 超过最大值 {total_max}")
                
                if total_max_int != config['total']:
                    errors.append(f"总分最大值不匹配: 期望 {config['total']}, 实际 {total_max_int}")
                    
            except ValueError:
                errors.append(f"总分格式错误: {total_value}")
    
    return errors


def re_score_question(question_type, question_id):
    """
    调用score_single_v2.py重新评分
    
    Args:
        question_type: 问题类型
        question_id: 问题ID
        
    Returns:
        bool: 是否成功
    """
    try:
        print(f"\n{'='*60}")
        print(f"重新评分: {question_type} - {question_id}")
        print(f"{'='*60}")
        
        # 调用score_single_v2.py
        result = subprocess.run(
            [sys.executable, SCORE_SINGLE_PATH, '--type', question_type, '--id', question_id],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✓ 重新评分成功")
            return True
        else:
            print(f"✗ 重新评分失败")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ 重新评分超时")
        return False
    except Exception as e:
        print(f"✗ 重新评分异常: {str(e)}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("自动修复第二轮评分错误")
    print("="*60)
    
    total_invalid = 0
    total_missing = 0
    total_re_scored = 0
    total_success = 0
    total_failed = 0
    
    for qtype in QUESTION_TYPES:
        # 检查中间文件
        intermediate_file = f'/path/to/AlloyDatasetBuilding/{qtype.capitalize()}/{qtype}_questions.json.intermediate_2-2'
        
        if not os.path.exists(intermediate_file):
            print(f"\n警告: 文件不存在 - {intermediate_file}")
            continue
        
        # 获取有问题的评分
        result = get_invalid_questions(intermediate_file, qtype)
        invalid_questions = result['invalid_questions']
        missing_scores = result['missing_scores']
        
        # 统计总数
        total_invalid += len(invalid_questions)
        total_missing += len(missing_scores)
        
        # 输出缺失评分的问题
        if missing_scores:
            print(f"\n{'='*60}")
            print(f"问题类型: {qtype}")
            print(f"{'='*60}")
            print(f"发现 {len(missing_scores)} 个缺失score2-2评分的问题:")
            
            for question_id, answer_fields in sorted(missing_scores.items()):
                print(f"\n  问题ID: {question_id}")
                for answer_field in answer_fields:
                    print(f"    - {answer_field} 缺失score2-2评分")
        
        # 输出有问题的问题
        if invalid_questions:
            print(f"\n{'='*60}")
            print(f"问题类型: {qtype}")
            print(f"{'='*60}")
            print(f"发现 {len(invalid_questions)} 个有问题的问题:")
            
            for question_id, issues in sorted(invalid_questions.items()):
                print(f"\n  问题ID: {question_id}")
                for issue in issues:
                    print(f"    - {issue['answer_field']}")
                    for error in issue['errors']:
                        print(f"      × {error}")
        
        # 重新评分缺失的评分
        if missing_scores:
            print(f"\n{'='*60}")
            print(f"开始重新评分缺失的评分...")
            print(f"{'='*60}")
            
            question_ids = sorted(missing_scores.keys())
            for question_id in tqdm(question_ids, desc=f"补评缺失 {qtype}", total=len(question_ids), unit="个"):
                total_re_scored += 1
                success = re_score_question(qtype, question_id)
                
                if success:
                    total_success += 1
                else:
                    total_failed += 1
        
        # 重新评分有问题的评分
        if invalid_questions:
            print(f"\n{'='*60}")
            print(f"开始重新评分有问题的评分...")
            print(f"{'='*60}")
            
            question_ids = sorted(invalid_questions.keys())
            for question_id in tqdm(question_ids, desc=f"重评错误 {qtype}", total=len(question_ids), unit="个"):
                total_re_scored += 1
                success = re_score_question(qtype, question_id)
                
                if success:
                    total_success += 1
                else:
                    total_failed += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    print(f"修复完成")
    print(f"{'='*60}")
    print(f"总问题类型数: {len(QUESTION_TYPES)}")
    print(f"总评分文件数: {len(QUESTION_TYPES)}")
    print(f"总缺失评分问题数: {total_missing}")
    print(f"总需要重新评分的问题数: {total_re_scored}")
    print(f"重新评分成功数: {total_success}")
    print(f"重新评分失败数: {total_failed}")
    print(f"成功率: {total_success/total_re_scored*100:.2f}%" if total_re_scored > 0 else "0.00%")
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
