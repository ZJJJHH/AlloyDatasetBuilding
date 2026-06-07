#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案生成系统 - 批量运行所有维度
运行方式: python run_all.py [--start 0] [--end 100] [--types all]
"""

import sys
import argparse
import subprocess
from answer_generator import get_answer_generator


def run_generation(question_type: str, start: int, end: int):
    """运行单个维度的答案生成"""
    print(f"\n{'='*60}")
    print(f"开始生成 {question_type} 类型问题的答案")
    print(f"{'='*60}\n")
    
    try:
        generator = get_answer_generator(question_type)
        generator.run(start_index=start, end_index=end)
        return True
    except Exception as e:
        print(f"\n生成 {question_type} 类型问题答案时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='批量生成所有维度的答案')
    parser.add_argument('--start', type=int, default=0, help='起始索引')
    parser.add_argument('--end', type=int, default=None, help='结束索引')
    parser.add_argument('--types', type=str, default='all', 
                       help='要生成的类型: all, what_if, causal, mitigation, pathway')
    parser.add_argument('--test', action='store_true', help='测试模式（仅处理前5个）')
    
    args = parser.parse_args()
    
    # 测试模式设置
    if args.test:
        end_index = 5
        print("=== 测试模式：仅处理前5个问题 ===")
    else:
        end_index = args.end
    
    # 确定要处理的类型
    if args.types == 'all':
        question_types = ['what_if', 'causal', 'mitigation', 'pathway']
    else:
        question_types = args.types.split(',')
    
    # 统计
    success_count = 0
    fail_count = 0
    
    # 依次处理每个类型
    for q_type in question_types:
        q_type = q_type.strip()
        if q_type not in ['what_if', 'causal', 'mitigation', 'pathway']:
            print(f"警告: 未知的问题类型 '{q_type}'，跳过")
            continue
        
        if run_generation(q_type, args.start, end_index):
            success_count += 1
        else:
            fail_count += 1
    
    # 总结
    print(f"\n{'='*60}")
    print(f"批量生成完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
