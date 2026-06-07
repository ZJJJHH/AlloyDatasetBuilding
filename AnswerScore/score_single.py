#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新评分单个样本脚本
用于对答案重新生成后的样本重新进行评分和优化
"""

import sys
import json
import argparse
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from score_generator import ScoreGenerator
from optimize_generator import OptimizeGenerator
from score_client import ScoreClient
from config import SCORE_MODEL


def load_questions(question_type: str) -> dict:
    """加载问题文件"""
    questions_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json"
    if not os.path.exists(questions_path):
        raise FileNotFoundError(f"问题文件不存在: {questions_path}")
    
    with open(questions_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def find_question_by_id(questions_data: dict, question_id: str) -> tuple:
    """
    根据question_id查找问题记录
    
    Args:
        questions_data: 问题数据字典
        question_id: 要查找的问题ID
        
    Returns:
        tuple: (问题索引, 问题记录)，如果未找到返回 (None, None)
    """
    questions = questions_data.get('questions', [])
    
    for idx, question in enumerate(questions):
        if question.get('question_id') == question_id:
            return idx, question
    
    return None, None


def score_single_question(question_type: str, question_id: str) -> bool:
    """
    重新评分单个问题
    
    Args:
        question_type: 问题类型
        question_id: 问题ID
        
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*60}")
    print(f"重新评分单个样本")
    print(f"{'='*60}")
    print(f"问题类型: {question_type}")
    print(f"问题ID: {question_id}")
    print(f"评分模型: {SCORE_MODEL}")
    print(f"{'='*60}\n")
    
    try:
        # 加载问题文件
        questions_data = load_questions(question_type)
        
        # 查找问题
        idx, question = find_question_by_id(questions_data, question_id)
        
        if idx is None:
            print(f"错误: 未找到问题ID '{question_id}'")
            return False
        
        print(f"找到问题，索引位置: {idx}")
        print(f"问题内容: {question.get('question_text', '')[:100]}...")
        
        # 检查是否已有评分
        has_scores = False
        for model in ['deepseek', 'qwen', 'minimax']:
            answer_key = f"answer_{model}"
            if answer_key in question and 'score' in question[answer_key]:
                has_scores = True
                print(f"警告: {answer_key} 已存在评分，将被覆盖")
        
        # 初始化评分器和优化器
        score_client = ScoreClient()
        score_generator = ScoreGenerator(score_client)
        optimize_generator = OptimizeGenerator(score_client)
        
        # 评分
        print(f"\n正在评分...")
        score_result = score_generator.score_question(question, question_type)
        
        if not score_result:
            print(f"错误: 评分失败")
            return False
        
        print(f"评分完成")
        
        # 将评分添加到问题中
        question = score_generator.add_scores_to_question(question, score_result)
        
        # 优化答案
        print(f"\n正在优化答案...")
        score_details = score_result['score_details']
        optimized_answer = optimize_generator.optimize_answer(question, question_type, score_details)
        
        if not optimized_answer:
            print(f"警告: 优化答案失败，跳过优化步骤")
        else:
            question = optimize_generator.update_question_with_optimized_answer(
                question, optimized_answer, question_type
            )
            print(f"优化完成")
        
        # 更新问题列表
        questions_data['questions'][idx] = question
        
        # 保存到原文件
        output_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json"
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 评分和优化结果已更新到: {output_path}")
        
        # 打印评分结果
        print(f"\n评分结果:")
        for model in ['deepseek', 'qwen', 'minimax']:
            answer_key = f"answer_{model}"
            if answer_key in question and 'score' in question[answer_key]:
                score = question[answer_key]['score']
                total = score.get('总分', 'N/A')
                print(f"  {model}: {total}")
        
        if f'answer_{SCORE_MODEL}_optimized' in question:
            print(f"  {SCORE_MODEL}_optimized: 已生成")
        
        # 保存统计信息
        stats = score_client.get_statistics()
        stats_path = output_path.replace('.json', f'_score_stats_{SCORE_MODEL}.json')
        with open(stats_path, 'w', encoding='utf-8-sig') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n统计信息已保存到: {stats_path}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"错误: {str(e)}")
        return False
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='重新评分单个样本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python score_single.py --type pathway --id pathway_000123
  python score_single.py --type what_if --id what_if_000456
  python score_single.py --type causal --id causal_000789
        '''
    )
    
    parser.add_argument('--type', type=str, required=True,
                       help='问题类型: what_if, causal, mitigation, pathway')
    parser.add_argument('--id', type=str, required=True,
                       help='问题ID（如: pathway_000123）')
    
    args = parser.parse_args()
    
    # 验证问题类型
    valid_types = ['what_if', 'causal', 'mitigation', 'pathway']
    if args.type not in valid_types:
        print(f"错误: 无效的问题类型 '{args.type}'")
        print(f"有效类型: {', '.join(valid_types)}")
        sys.exit(1)
    
    # 执行重新评分
    success = score_single_question(args.type, args.id)
    
    if success:
        print(f"\n{'='*60}")
        print(f"✓ 重新评分完成!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print(f"✗ 重新评分失败!")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
