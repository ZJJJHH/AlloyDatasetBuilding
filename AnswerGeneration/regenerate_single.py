#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成单个样本答案脚本
用于对评分阶段发现的错误样本重新生成答案
"""

import sys
import json
import argparse
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from answer_generator import get_answer_generator
from config import LLM_MODEL


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


def regenerate_single_answer(question_type: str, question_id: str, 
                            model: str = None) -> bool:
    """
    重新生成单个问题的答案
    
    Args:
        question_type: 问题类型
        question_id: 问题ID
        model: 使用的模型（可选，覆盖config中的配置）
        
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*60}")
    print(f"重新生成单个答案")
    print(f"{'='*60}")
    print(f"问题类型: {question_type}")
    print(f"问题ID: {question_id}")
    print(f"模型: {model or LLM_MODEL}")
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
        
        # 检查是否已有答案
        answer_key = f"answer_{LLM_MODEL if model is None else model}"
        if answer_key in question:
            print(f"警告: 已存在 {answer_key} 答案，将被覆盖")
        
        # 创建临时生成器
        generator = get_answer_generator(question_type)
        
        # 生成新答案
        print(f"\n正在生成新答案...")
        answer = generator.generate_answer(question)
        
        # 更新问题记录
        updated_question = generator._save_answer_to_question(question, answer)
        
        # 保存到原文件
        questions_data['questions'][idx] = updated_question
        
        output_path = f"/path/to/AlloyDatasetBuilding/{question_type.capitalize()}/{question_type}_questions.json"
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 答案已更新到: {output_path}")
        print(f"答案内容预览: {answer.get('content', '')[:200]}...")
        
        # 保存统计信息
        stats = generator.llm_client.get_statistics()
        stats_path = output_path.replace('.json', f'_answer_stats_{LLM_MODEL if model is None else model}.json')
        with open(stats_path, 'w', encoding='utf-8-sig') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"统计信息已保存到: {stats_path}")
        
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
        description='重新生成单个样本的答案',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python regenerate_single.py --type pathway --id pathway_000123
  python regenerate_single.py --type what_if --id what_if_000456 --model deepseek
  python regenerate_single.py --type causal --id causal_000789 --model qwen
        '''
    )
    
    parser.add_argument('--type', type=str, required=True,
                       help='问题类型: what_if, causal, mitigation, pathway')
    parser.add_argument('--id', type=str, required=True,
                       help='问题ID（如: pathway_000123）')
    parser.add_argument('--model', type=str, default=None,
                       help='使用的模型: deepseek, qwen, glm, minimax（可选，默认使用config.py中的配置）')
    
    args = parser.parse_args()
    
    # 验证问题类型
    valid_types = ['what_if', 'causal', 'mitigation', 'pathway']
    if args.type not in valid_types:
        print(f"错误: 无效的问题类型 '{args.type}'")
        print(f"有效类型: {', '.join(valid_types)}")
        sys.exit(1)
    
    # 验证模型
    if args.model is not None:
        valid_models = ['deepseek', 'qwen', 'glm', 'minimax']
        if args.model not in valid_models:
            print(f"错误: 无效的模型 '{args.model}'")
            print(f"有效模型: {', '.join(valid_models)}")
            sys.exit(1)
    
    # 执行重新生成
    success = regenerate_single_answer(args.type, args.id, args.model)
    
    if success:
        print(f"\n{'='*60}")
        print(f"✓ 重新生成完成!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print(f"✗ 重新生成失败!")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
