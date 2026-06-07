#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证第二轮评分结果
"""
import json
import re
from collections import defaultdict

# 评分维度配置（与AnswerScore2/config.py保持一致）
SCORE_CONFIGS = {
    'what_if': {
        'dimensions': {
            '方案可行性': 30,
            '技术合理性': 30,
            '数据支持度': 20,
            '方案多样性': 10,
            '表达清晰度': 10
        },
        'total': 100
    },
    'causal': {
        'dimensions': {
            '因果关系正确性': 30,
            '机理解释深度': 30,
            '专业术语使用': 20,
            '逻辑连贯性': 20
        },
        'total': 100
    },
    'mitigation': {
        'dimensions': {
            '问题诊断准确性': 30,
            '解决方案可行性': 30,
            '系统性': 20,
            '可操作性': 20
        },
        'total': 100
    },
    'pathway': {
        'dimensions': {
            '路径完整性': 30,
            '机理清晰度': 30,
            '逻辑连贯性': 20,
            '专业深度': 20
        },
        'total': 100
    }
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
                
                # 验证总分是否等于各维度之和
                calculated_total = 0
                for dimension, max_score in dimensions.items():
                    if dimension in score_entry:
                        value = score_entry[dimension]
                        if isinstance(value, str) and '/' in value:
                            try:
                                score, _ = value.split('/')
                                calculated_total += int(score)
                            except ValueError:
                                pass
                
                if calculated_total != total_score_int:
                    errors.append(f"总分不一致: 计算得 {calculated_total}, 实际 {total_score_int}")
                    
            except ValueError:
                errors.append(f"总分格式错误: {total_value}")
    
    return errors

def validate_scores_in_file(file_path, question_type):
    """
    验证文件中的所有评分
    
    Args:
        file_path: 文件路径
        question_type: 问题类型
    
    Returns:
        dict: 验证结果统计
    """
    print(f"\n{'='*60}")
    print(f"验证评分文件: {file_path}")
    print(f"{'='*60}\n")
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    
    total_questions = len(questions)
    total_answers = 0
    questions_with_errors = 0
    total_errors = 0
    error_details = defaultdict(list)
    missing_scores = defaultdict(list)
    
    answer_fields = ['answer_deepseek', 'answer_qwen', 'answer_minimax', 'answer_glm-5_optimized']
    
    for question in questions:
        question_id = question.get('question_id', '')
        has_errors = False
        
        for answer_field in answer_fields:
            if answer_field in question:
                answer = question[answer_field]
                if isinstance(answer, dict):
                    # 检查score2-2字段是否直接在answer下
                    if 'score2-2' in answer:
                        score2_1 = answer['score2-2']
                        if isinstance(score2_1, dict):
                            total_answers += 1
                            errors = validate_score_entry(score2_1, question_type)
                            
                            if errors:
                                has_errors = True
                                total_errors += len(errors)
                                error_details[question_id].extend([
                                    f"  [{answer_field}] {error}" for error in errors
                                ])
                    # 也检查score字段下的score2-2（兼容旧格式）
                    elif 'score' in answer and isinstance(answer['score'], dict):
                        if 'score2-2' in answer['score']:
                            score2_1 = answer['score']['score2-2']
                            if isinstance(score2_1, dict):
                                total_answers += 1
                                errors = validate_score_entry(score2_1, question_type)
                                
                                if errors:
                                    has_errors = True
                                    total_errors += len(errors)
                                    error_details[question_id].extend([
                                        f"  [{answer_field}] {error}" for error in errors
                                    ])
                    # 检查缺失的score2-2
                    else:
                        missing_scores[question_id].append(answer_field)
        
        if has_errors:
            questions_with_errors += 1
    
    # 输出统计结果
    print(f"统计结果:")
    print(f"  总问题数: {total_questions}")
    print(f"  总评分条目数: {total_answers}")
    print(f"  总应有评分条目数: {total_questions * 4}")
    print(f"  评分条目缺失数: {total_questions * 4 - total_answers}")
    print(f"  有问题的问题数: {questions_with_errors}")
    print(f"  总错误数: {total_errors}")
    print(f"  错误率: {total_errors/total_answers*100:.2f}%" if total_answers > 0 else "  错误率: 0.00%")
    
    # 输出缺失的评分
    if missing_scores:
        print(f"\n缺失score2-2评分的问题:")
        for question_id, missing_fields in sorted(missing_scores.items()):
            print(f"  问题ID: {question_id}")
            for field in missing_fields:
                print(f"    - {field}")
    
    # 输出错误详情
    if error_details:
        print(f"\n错误详情:")
        for question_id, errors in sorted(error_details.items()):
            print(f"\n  问题ID: {question_id}")
            for error in errors:
                print(error)
    else:
        print(f"\n✓ 所有评分条目均符合规范！")
    
    return {
        'total_questions': total_questions,
        'total_answers': total_answers,
        'questions_with_errors': questions_with_errors,
        'total_errors': total_errors,
        'error_details': error_details,
        'missing_scores': missing_scores
    }

# 验证所有问题类型的评分
question_types = ['what_if', 'causal', 'mitigation', 'pathway']

for qtype in question_types:
    # 检查中间文件
    intermediate_file = f'/path/to/AlloyDatasetBuilding/{qtype.capitalize()}/{qtype}_questions.json.intermediate_2-2'
    
    try:
        validate_scores_in_file(intermediate_file, qtype)
    except FileNotFoundError:
        print(f"\n警告: 文件不存在 - {intermediate_file}")
    except Exception as e:
        print(f"\n错误: {str(e)}")

print(f"\n{'='*60}")
print(f"✓ 所有文件验证完成!")
print(f"{'='*60}")
