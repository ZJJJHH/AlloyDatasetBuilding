#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量评分和优化脚本 - 为所有问题类型的问题进行评分和优化
支持增量更新和全量覆盖
"""

import json
import os
import sys
import shutil
from typing import Dict, Any, Optional
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import SCORE_MODEL
from score_client import ScoreClient
from score_generator import ScoreGenerator
from optimize_generator import OptimizeGenerator


class ScoreProcessor:
    """评分处理器"""
    
    def __init__(self):
        self.client = ScoreClient()
        self.score_generator = ScoreGenerator(self.client)
        self.optimize_generator = OptimizeGenerator(self.client)
        
        self.question_types = ['what_if', 'causal', 'mitigation', 'pathway']
        
        self.base_dir = '/path/to/AlloyDatasetBuilding'
        self.output_dir = '/path/to/AlloyDatasetBuilding/AnswerScore'
    
    def get_question_file(self, question_type: str) -> str:
        """获取问题文件路径"""
        question_type_map = {
            'what_if': 'What_if/what_if_questions.json',
            'causal': 'Causal/causal_questions.json',
            'mitigation': 'Mitigation/mitigation_questions.json',
            'pathway': 'Pathway/pathway_questions.json'
        }
        
        return os.path.join(self.base_dir, question_type_map.get(question_type, ''))
    
    def get_intermediate_file(self, question_type: str) -> str:
        """获取中间文件路径"""
        original_file = self.get_question_file(question_type)
        return original_file + ".intermediate"
    
    def ensure_intermediate_file(self, question_type: str):
        """确保中间文件存在，如果不存在则从原文件复制"""
        original_file = self.get_question_file(question_type)
        intermediate_file = self.get_intermediate_file(question_type)
        
        # 如果中间文件不存在，从原文件复制
        if not os.path.exists(intermediate_file) and os.path.exists(original_file):
            try:
                with open(original_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                with open(intermediate_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  已创建中间文件: {intermediate_file}")
            except Exception as e:
                print(f"  警告：创建中间文件失败: {str(e)}")
    
    def clean_incremental_files(self):
        """清理所有中间文件"""
        for question_type in self.question_types:
            intermediate_file = self.get_intermediate_file(question_type)
            if os.path.exists(intermediate_file):
                os.remove(intermediate_file)
                print(f"已清理中间文件: {intermediate_file}")
        print("所有中间文件清理完成")
    
    def load_questions(self, question_type: str) -> list:
        """加载问题"""
        file_path = self.get_question_file(question_type)
        
        if not os.path.exists(file_path):
            print(f"警告：问题文件不存在: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # 问题文件可能是直接的列表，也可能是包含questions键的对象
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('questions', [])
        
        return []
    
    def save_questions(self, questions: list, question_type: str, 
                      is_incremental: bool = False,
                      start_idx: int = 0) -> str:
        """保存问题"""
        if is_incremental:
            file_path = self.get_intermediate_file(question_type)
        else:
            file_path = self.get_question_file(question_type)
        
        # 加载原数据结构（如果是增量保存）
        if is_incremental and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                
                # 如果是对象格式，更新questions列表
                if isinstance(data, dict):
                    existing_questions = data.get('questions', [])
                    
                    # 覆盖指定范围的问题
                    for idx, question in enumerate(questions):
                        global_idx = start_idx + idx
                        if global_idx < len(existing_questions):
                            existing_questions[global_idx] = question
                        else:
                            existing_questions.append(question)
                    
                    data['questions'] = existing_questions
                    with open(file_path, 'w', encoding='utf-8-sig') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return file_path
                # 如果是列表格式
                elif isinstance(data, list):
                    # 覆盖指定范围的问题
                    for idx, question in enumerate(questions):
                        global_idx = start_idx + idx
                        if global_idx < len(data):
                            data[global_idx] = question
                        else:
                            data.append(question)
                    with open(file_path, 'w', encoding='utf-8-sig') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return file_path
            except Exception as e:
                print(f"  警告：保存中间文件失败: {str(e)}")
        
        # 直接保存为列表格式
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def process_single_question(self, question: Dict[str, Any], question_type: str) -> Optional[Dict[str, Any]]:
        """处理单个问题"""
        try:
            score_result = self.score_generator.score_question(question, question_type)
            
            if not score_result:
                print(f"评分失败: {question.get('question_id', 'unknown')}")
                return question
            
            question = self.score_generator.add_scores_to_question(question, score_result)
            
            score_details = score_result['score_details']
            optimized_answer = self.optimize_generator.optimize_answer(
                question, question_type, score_details
            )
            
            if optimized_answer:
                question = self.optimize_generator.update_question_with_optimized_answer(
                    question, optimized_answer, question_type
                )
            
            return question
        
        except Exception as e:
            print(f"处理问题失败 {question.get('question_id', 'unknown')}: {str(e)}")
            return question
    
    def process_question_type(self, question_type: str, 
                             start_idx: int = 0, 
                             end_idx: int = None) -> int:
        """处理单个问题类型的所有问题"""
        questions = self.load_questions(question_type)
        
        if not questions:
            print(f"警告：{question_type} 问题列表为空")
            return 0
        
        if end_idx is None:
            end_idx = len(questions)
        
        # ✅ 确保中间文件存在（从原文件复制）
        self.ensure_intermediate_file(question_type)
        
        # 只处理指定范围的问题
        questions_to_process = questions[start_idx:end_idx]
        total = len(questions_to_process)
        
        processed = 0
        for idx, question in enumerate(tqdm(questions_to_process, desc=f"处理 {question_type}", unit="question")):
            question_idx = start_idx + idx
            
            question = self.process_single_question(question, question_type)
            
            questions_to_process[idx] = question
            processed += 1
            
            if processed % 10 == 0:
                # ✅ 保存到中间文件（覆盖指定位置）
                self.save_questions(questions_to_process[:processed], question_type, 
                                   is_incremental=True, start_idx=start_idx)
                print(f"  已处理 {processed}/{total} 个问题，已保存中间文件")
        
        # 保存最终结果到中间文件
        self.save_questions(questions_to_process, question_type, 
                           is_incremental=True, start_idx=start_idx)
        
        print(f"  {question_type} 处理完成，共处理 {processed} 个问题")
        print(f"  中间文件已保存: {self.get_intermediate_file(question_type)}")
        print(f"  请检查中间文件后再决定是否覆盖原文件")
        
        return processed
    
    def run_all(self, question_types: list = None, 
               start_idx: int = 0, end_idx: int = None) -> Dict[str, int]:
        """处理所有问题类型"""
        if question_types is None:
            question_types = self.question_types
        
        results = {}
        
        for question_type in question_types:
            if question_type not in self.question_types:
                print(f"警告：未知的问题类型 '{question_type}'")
                continue
            
            print(f"\n{'='*60}")
            print(f"开始处理 {question_type} 问题")
            print(f"{'='*60}")
            
            processed = self.process_question_type(question_type, start_idx, end_idx)
            results[question_type] = processed
        
        print(f"\n{'='*60}")
        print("所有问题类型处理完成")
        print(f"{'='*60}")
        
        for question_type, count in results.items():
            print(f"  {question_type}: {count} 个问题")
        
        return results


if __name__ == "__main__":
    print("="*60)
    print("答案评分和优化系统")
    print("="*60)
    
    processor = ScoreProcessor()
    
    print(f"\n评分模型: {SCORE_MODEL}")
    print(f"支持的问题类型: {processor.question_types}")
    
    import argparse
    parser = argparse.ArgumentParser(description='批量评分和优化')
    parser.add_argument('--types', type=str, default=None,
                       help='要处理的问题类型，多个类型用逗号分隔')
    parser.add_argument('--start', type=int, default=0,
                       help='起始索引')
    parser.add_argument('--end', type=int, default=None,
                       help='结束索引')
    parser.add_argument('--clean', action='store_true',
                       help='清理中间文件')
    
    args = parser.parse_args()
    
    if args.clean:
        processor.clean_incremental_files()
        exit(0)
    
    question_types = None
    if args.types:
        question_types = [t.strip() for t in args.types.split(',')]
    
    results = processor.run_all(question_types, args.start, args.end)
    
    stats = processor.client.get_statistics()
    print(f"\nAPI调用统计: {stats}")
