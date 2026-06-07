#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失效诊断问答案生成脚本
运行方式: python generate_mitigation_answers.py [--start 0] [--end 100]
"""

import sys
import argparse
from answer_generator import get_answer_generator


def main():
    parser = argparse.ArgumentParser(description='生成失效诊断问答案')
    parser.add_argument('--start', type=int, default=0, help='起始索引')
    parser.add_argument('--end', type=int, default=None, help='结束索引')
    parser.add_argument('--test', action='store_true', help='测试模式（仅处理前5个）')
    
    args = parser.parse_args()
    
    if args.test:
        end_index = 5
        print("=== 测试模式：仅处理前5个问题 ===")
    else:
        end_index = args.end
    
    try:
        generator = get_answer_generator('mitigation')
        generator.run(start_index=args.start, end_index=end_index)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
