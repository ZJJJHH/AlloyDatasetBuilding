#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新评分单个样本脚本（第二轮评分）
用于对不符合规范的评分重新生成
"""

import sys
import json
import argparse
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from score_generator import ScoreGenerator
from score_client import ScoreClient
from config import SCORE_MODEL


def load_intermediate_questions(question_type: str) -> dict:
    """加载中间问题文件"""
    questions_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json.intermediate_2-2"
    if not os.path.exists(questions_path):
        raise FileNotFoundError(f"中间问题文件不存在: {questions_path}")
    
    with open(questions_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def load_original_questions(question_type: str) -> dict:
    """加载原始问题文件"""
    questions_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json"
    if not os.path.exists(questions_path):
        raise FileNotFoundError(f"原始问题文件不存在: {questions_path}")
    
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


def score_single_question_v2(question_type: str, question_id: str, 
                             use_intermediate: bool = True) -> bool:
    """
    重新评分单个问题（第二轮）
    
    Args:
        question_type: 问题类型
        question_id: 问题ID
        use_intermediate: 是否使用中间文件
        
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*60}")
    print(f"重新评分单个样本（第二轮评分）")
    print(f"{'='*60}")
    print(f"问题类型: {question_type}")
    print(f"问题ID: {question_id}")
    print(f"评分模型: {SCORE_MODEL}")
    print(f"{'='*60}\n")
    
    try:
        # 加载问题文件
        if use_intermediate:
            questions_data = load_intermediate_questions(question_type)
            file_type = "中间文件"
            output_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json.intermediate_2-2"
        else:
            questions_data = load_original_questions(question_type)
            file_type = "原始文件"
            output_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json"
        
        # 查找问题
        idx, question = find_question_by_id(questions_data, question_id)
        
        if idx is None:
            print(f"错误: 未找到问题ID '{question_id}'")
            return False
        
        print(f"找到问题，索引位置: {idx}")
        print(f"文件类型: {file_type}")
        print(f"问题内容: {question.get('question_text', '')[:100]}...")
        
        # 检查是否已有score2-2评分
        has_score2_2 = False
        for model in ['deepseek', 'qwen', 'minimax', 'glm-5_optimized']:
            answer_key = f"answer_{model}"
            if answer_key in question and 'score2-2' in question[answer_key]:
                has_score2_2 = True
                print(f"警告: {answer_key} 已存在score2-2评分，将被覆盖")
        
        # 初始化评分器
        score_client = ScoreClient()
        score_generator = ScoreGenerator(score_client)
        
        # 评分
        print(f"\n正在评分...")
        score_result = score_generator.score_question(question, question_type)
        
        if not score_result:
            print(f"错误: 评分失败")
            return False
        
        print(f"评分完成")
        
        # 将评分添加到问题中
        question = score_generator.add_scores_to_question(question, score_result, question_type)
        
        # 更新问题列表
        questions_data['questions'][idx] = question
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 评分结果已更新到: {output_path}")
        
        # 打印评分结果
        print(f"\n评分结果:")
        answer_mappings = {
            'answer_deepseek': 'DeepSeek',
            'answer_qwen': 'Qwen',
            'answer_minimax': 'MiniMax',
            'answer_glm-5_optimized': 'GLM-5 Optimized'
        }
        
        for answer_key, model_name in answer_mappings.items():
            if answer_key in question and 'score2-2' in question[answer_key]:
                score = question[answer_key]['score2-2']
                total = score.get('总分', 'N/A')
                print(f"  {model_name}: {total}")
        
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
        description='重新评分单个样本（第二轮评分）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python score_single_v2.py --type pathway --id pathway_000123
  python score_single_v2.py --type what_if --id what_if_000456
  python score_single_v2.py --type causal --id causal_000789
  python score_single_v2.py --type causal --id causal_000004 --original
        '''
    )
    
    parser.add_argument('--type', type=str, required=True,
                       help='问题类型: what_if, causal, mitigation, pathway')
    parser.add_argument('--id', type=str, required=True,
                       help='问题ID（如: pathway_000123）')
    parser.add_argument('--original', action='store_true',
                       help='使用原始问题文件而不是中间文件')
    
    args = parser.parse_args()
    
    # 验证问题类型
    valid_types = ['what_if', 'causal', 'mitigation', 'pathway']
    if args.type not in valid_types:
        print(f"错误: 无效的问题类型 '{args.type}'")
        print(f"有效类型: {', '.join(valid_types)}")
        sys.exit(1)
    
    # 执行重新评分
    success = score_single_question_v2(args.type, args.id, use_intermediate=not args.original)
    
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
