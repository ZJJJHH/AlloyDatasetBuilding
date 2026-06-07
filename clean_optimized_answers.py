#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清洗GLM-5优化答案中的旁白性语句
"""

import json
import re
import os
import sys


def clean_optimized_answer_content(content: str) -> str:
    """
    清洗GLM-5优化答案中的旁白性语句
    
    Args:
        content: 原始答案内容
    
    Returns:
        清洗后的答案内容
    """
    if not content:
        return content
    
    lines = content.split('\n')
    
    # 匹配旁白性语句的正则表达式
    # 1. "根据您的要求，我综合了..." 类型的语句
    # 2. "我综合了三个答案的优势..." 类型的语句
    # 3. "特别是采用了..." 类型的语句
    # 4. "融合了..." 类型的语句
    # 5. "形成了以下最优答案。" 类型的语句
    
    # 要删除的旁白模式
    bypass_patterns = [
        r'^根据您的要求，我综合了.*?形成了以下最优答案。?$',  # "根据您的要求，我综合了...形成了以下最优答案。"
        r'^我综合了三个答案的优势.*?$',  # "我综合了三个答案的优势..."
        r'^特别是采用了.*?$',  # "特别是采用了..."
        r'^融合了.*?$',  # "融合了..."
        r'^以及.*?$',  # "以及..."
        r'^形成了以下.*?$',  # "形成了以下..."
        r'^根据.*?要求.*?$',  # "根据...要求..."
        r'^我.*?综合.*?优势.*?$',  # "我...综合...优势..."
        r'^基于.*?综合.*?$',  # "基于...综合..."
        r'^在.*?基础上.*?$',  # "在...基础上..."
        r'^参考了.*?$',  # "参考了..."
        r'^借鉴了.*?$',  # "借鉴了..."
        r'^结合了.*?$',  # "结合了..."
        r'^优化后的答案.*?$',  # "优化后的答案..."
        r'^综合优化.*?$',  # "综合优化..."
        r'^以下是.*?答案.*?$',  # "以下是...答案..."
        r'^以下是优化后的.*?$',  # "以下是优化后的..."
        r'^以下是综合.*?$',  # "以下是综合..."
        r'^\*\*最优综合答案：?\*\*$',  # "**最优综合答案：**"
        r'^\*\*综合优化答案：?\*\*$',  # "**综合优化答案：**"
        r'^\*\*最优答案：?\*\*$',  # "**最优答案：**"
        r'^\*\*优化后的答案：?\*\*$',  # "**优化后的答案：**"
        r'^\*\*综合答案：?\*\*$',  # "**综合答案：**"
        r'^\*\*最优综合答案.*?\*\*$',  # "**最优综合答案...**"
        r'^\*\*综合优化答案.*?\*\*$',  # "**综合优化答案...**"
        r'^\*\*最优答案.*?\*\*$',  # "**最优答案...**"
        r'^\*\*优化后的答案.*?\*\*$',  # "**优化后的答案...**"
        r'^\*\*综合答案.*?\*\*$',  # "**综合答案...**"
        r'^\*\*以下.*?答案.*?\*\*$',  # "**以下...答案...**"
        r'^\*\*综合.*?答案.*?\*\*$',  # "**综合...答案...**"
        r'^\*\*优化.*?答案.*?\*\*$',  # "**优化...答案...**"
        r'^\*\*最优.*?答案.*?\*\*$',  # "**最优...答案...**"
        r'^\*\*最佳.*?答案.*?\*\*$',  # "**最佳...答案...**"
        r'^\*\*答案.*?：?\*\*$',  # "**答案：**"
        r'^\*\*最优.*?\*\*$',  # "**最优...**"
        r'^\*\*综合.*?综合.*?\*\*$',  # "**综合...综合...**"
        r'^\*\*优化.*?优化.*?\*\*$',  # "**优化...优化...**"
        r'^\*\*以下.*?答案.*?\*\*$',  # "**以下...答案...**"
        r'^### 最优综合答案$',  # "### 最优综合答案"
        r'^### 综合优化答案$',  # "### 综合优化答案"
        r'^### 最优答案$',  # "### 最优答案"
        r'^### 优化后的答案$',  # "### 优化后的答案"
        r'^### 综合答案$',  # "### 综合答案"
        r'^### 最优综合答案.*?$',  # "### 最优综合答案..."
        r'^### 综合优化答案.*?$',  # "### 综合优化答案..."
        r'^### 最优答案.*?$',  # "### 最优答案..."
        r'^### 优化后的答案.*?$',  # "### 优化后的答案..."
        r'^### 综合答案.*?$',  # "### 综合答案..."
        r'^### 以下.*?答案.*?$',  # "### 以下...答案..."
        r'^### 综合.*?答案.*?$',  # "### 综合...答案..."
        r'^### 优化.*?答案.*?$',  # "### 优化...答案..."
        r'^### 最优.*?答案.*?$',  # "### 最优...答案..."
        r'^### 最佳.*?答案.*?$',  # "### 最佳...答案..."
        r'^### 最优综合答案$',  # "### 最优综合答案"
        r'^### 综合优化答案$',  # "### 综合优化答案"
        r'^### 最优答案$',  # "### 最优答案"
        r'^### 优化后的答案$',  # "### 优化后的答案"
        r'^### 综合答案$',  # "### 综合答案"
        r'^最优综合答案：?$',  # "最优综合答案："
        r'^综合优化答案：?$',  # "综合优化答案："
        r'^最优答案：?$',  # "最优答案："
        r'^优化后的答案：?$',  # "优化后的答案："
        r'^综合答案：?$',  # "综合答案："
        r'^最优综合答案.*?$',  # "最优综合答案..."
        r'^综合优化答案.*?$',  # "综合优化答案..."
        r'^最优答案.*?$',  # "最优答案..."
        r'^优化后的答案.*?$',  # "优化后的答案..."
        r'^综合答案.*?$',  # "综合答案..."
        r'^以下.*?答案.*?$',  # "以下...答案..."
        r'^综合.*?答案.*?$',  # "综合...答案..."
        r'^优化.*?答案.*?$',  # "优化...答案..."
        r'^最优.*?答案.*?$',  # "最优...答案..."
        r'^最佳.*?答案.*?$',  # "最佳...答案..."
        r'^答案.*?：?$',  # "答案："
        r'^最优.*?$',  # "最优..."
        r'^综合.*?综合.*?$',  # "综合...综合..."
        r'^优化.*?优化.*?$',  # "优化...优化..."
        r'^以下.*?答案.*?$',  # "以下...答案..."
    ]
    
    cleaned_lines = []
    skip_next_empty = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # 检查是否是旁白性语句
        is_bypass = False
        for pattern in bypass_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_bypass = True
                break
        
        # 跳过旁白性语句
        if is_bypass:
            skip_next_empty = True
            continue
        
        # 跳过旁白后紧跟的空行
        if skip_next_empty and line_stripped == '':
            skip_next_empty = False
            continue
        
        skip_next_empty = False
        cleaned_lines.append(line)
    
    # 合并清洗后的行
    cleaned_content = '\n'.join(cleaned_lines)
    
    # 移除开头多余的空行
    cleaned_content = cleaned_content.lstrip('\n')
    
    return cleaned_content


def clean_file(file_path: str, output_path: str = None) -> int:
    """
    清洗文件中的GLM-5优化答案
    
    Args:
        file_path: 输入文件路径
        output_path: 输出文件路径，如果为None则覆盖原文件
    
    Returns:
        清洗的答案数量
    """
    if output_path is None:
        output_path = file_path
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    cleaned_count = 0
    
    # 处理不同格式的数据
    if isinstance(data, dict):
        questions = data.get('questions', [])
    elif isinstance(data, list):
        questions = data
    else:
        print(f"未知的数据格式: {type(data)}")
        return 0
    
    for question in questions:
        if 'answer_glm-5_optimized' in question:
            original_content = question['answer_glm-5_optimized'].get('content', '')
            cleaned_content = clean_optimized_answer_content(original_content)
            
            if original_content != cleaned_content:
                question['answer_glm-5_optimized']['content'] = cleaned_content
                cleaned_count += 1
                print(f"清洗问题: {question.get('question_id', 'unknown')}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return cleaned_count


def main():
    """主函数"""
    base_dir = '/path/to/AlloyDatasetBuilding'
    question_types = ['what_if', 'property_lookup', 'causal', 'mitigation', 'pathway']
    
    for question_type in question_types:
        if question_type == 'pathway':
            file_name = 'pathway_questions.json'
            dir_name = 'Pathway'
        elif question_type == 'property_lookup':
            file_name = 'property_lookup_questions.json'
            dir_name = 'PropertyLookup'
        else:
            file_name = f'{question_type}_questions.json'
            dir_name = question_type.capitalize()
        
        file_path = os.path.join(base_dir, dir_name, file_name)
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue
        
        print(f"\n处理文件: {file_path}")
        cleaned_count = clean_file(file_path)
        print(f"清洗了 {cleaned_count} 个答案")
    
    # 处理中间文件
    intermediate_file = os.path.join(base_dir, 'Pathway', 'pathway_questions.json.intermediate_2-1')
    if os.path.exists(intermediate_file):
        print(f"\n处理中间文件: {intermediate_file}")
        cleaned_count = clean_file(intermediate_file)
        print(f"清洗了 {cleaned_count} 个答案")


if __name__ == "__main__":
    main()
