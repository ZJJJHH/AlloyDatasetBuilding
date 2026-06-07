#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因果问生成器启动脚本
支持命令行参数和进度条显示
"""

import argparse
import json
import os
import sys
import time
from generate_causal_questions import CausalQuestionGenerator, save_questions_to_json
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient, MockDeepSeekClient


def create_progress_bar(total: int, desc: str = "生成进度"):
    """创建进度条"""
    try:
        from tqdm import tqdm
        return tqdm(total=total, desc=desc, unit="条", ncols=100)
    except ImportError:
        print("提示：未安装tqdm库，使用简单进度显示")
        return None


def simple_progress_update(current: int, total: int, start_time: float):
    """简单进度显示"""
    elapsed_time = time.time() - start_time
    progress = current / total * 100
    
    if current > 0:
        speed = current / elapsed_time * 60  # 条/分钟
        remaining_time = (total - current) / speed * 60  # 秒
        
        print(f"生成进度: {current}/{total} ({progress:.1f}%) | "
              f"速度: {speed:.1f}条/分钟 | "
              f"预计剩余: {remaining_time/60:.1f}分钟", end="\r")
    
    if current == total:
        print()  # 换行


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    else:
        print(f"警告：配置文件 {config_path} 不存在，使用默认配置")
        return {
            "generation_config": {
                "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
                "output_path": "/path/to/AlloyDatasetBuilding/Causal/causal_questions.json",
                "target_question_count": 1000,
                "batch_size": 3,
                "api_delay": 1.5
            },
            "deepseek_config": {
                "api_key": "YOUR_DEEPSEEK_API_KEY_HERE",
                "max_tokens": 200,
                "temperature": 0.7
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="因果问问题生成器")
    parser.add_argument("--config", default="config.json", 
                       help="配置文件路径")
    parser.add_argument("--count", type=int, default=1000,
                       help="生成问题数量")
    parser.add_argument("--output", 
                       help="输出文件路径")
    parser.add_argument("--mock", action="store_true",
                       help="使用模拟客户端（测试模式）")
    parser.add_argument("--test", action="store_true",
                       help="测试模式（生成少量问题）")
    parser.add_argument("--no-progress", action="store_true",
                       help="禁用进度条")
    
    args = parser.parse_args()
    
    print("=== 因果问问题生成器 ===")
    
    # 加载配置
    config = load_config(args.config)
    
    # 处理命令行参数
    if args.count:
        config["generation_config"]["target_question_count"] = args.count
    
    if args.output:
        config["generation_config"]["output_path"] = args.output
    
    if args.test:
        config["generation_config"]["target_question_count"] = 10
        print(f"测试模式：生成{config['generation_config']['target_question_count']}个问题")
    
    target_count = config["generation_config"]["target_question_count"]
    
    # 检查数据文件
    rag_data_path = config["generation_config"]["rag_data_path"]
    if not os.path.exists(rag_data_path):
        print(f"错误：RAG数据文件不存在: {rag_data_path}")
        sys.exit(1)
    
    # 初始化组件
    print("初始化组件...")
    
    # 初始化RAG检索器
    try:
        rag_retriever = RAGRetriever(rag_data_path)
        print("✓ RAG检索器初始化成功")
    except Exception as e:
        print(f"✗ RAG检索器初始化失败: {str(e)}")
        sys.exit(1)
    
    # 初始化DeepSeek客户端
    if args.mock:
        deepseek_client = MockDeepSeekClient()
        print("✓ 模拟DeepSeek客户端初始化成功（测试模式）")
    else:
        api_key = config["deepseek_config"]["api_key"]
        if api_key == "YOUR_DEEPSEEK_API_KEY_HERE":
            print("错误：请先在config.json中配置您的DeepSeek API密钥")
            print("或者使用 --mock 参数进行测试")
            sys.exit(1)
        
        try:
            deepseek_client = DeepSeekClient(api_key)
            print("✓ DeepSeek客户端初始化成功")
        except Exception as e:
            print(f"✗ DeepSeek客户端初始化失败: {str(e)}")
            sys.exit(1)
    
    # 初始化问题生成器
    try:
        generator = CausalQuestionGenerator(rag_retriever, deepseek_client)
        print("✓ 问题生成器初始化成功")
    except Exception as e:
        print(f"✗ 问题生成器初始化失败: {str(e)}")
        sys.exit(1)
    
    # 创建进度条
    progress_bar = None
    if not args.no_progress:
        progress_bar = create_progress_bar(target_count, "因果问生成进度")
    
    # 生成问题
    print(f"开始生成 {target_count} 个因果问问题...")
    start_time = time.time()
    
    try:
        # 使用进度条生成问题
        questions = generator.generate_batch_questions(target_count, progress_bar)
        
        # 关闭进度条
        if progress_bar:
            progress_bar.close()
        
        # 保存结果
        output_path = config["generation_config"]["output_path"]
        save_questions_to_json(questions, output_path)
        
        # 显示统计信息
        total_time = time.time() - start_time
        print(f"\n=== 生成统计 ===")
        print(f"总问题数: {len(questions)}")
        
        # API调用统计
        api_stats = deepseek_client.get_statistics()
        print(f"\nAPI调用统计:")
        for key, value in api_stats.items():
            print(f"  {key}: {value}")
        
        # 因果关系类型分布
        causal_types = {}
        for q in questions:
            c_type = q['causal_scenario']['causal_type']
            causal_types[c_type] = causal_types.get(c_type, 0) + 1
        
        print(f"\n因果关系类型分布:")
        for c_type, count in causal_types.items():
            percentage = count / len(questions) * 100
            print(f"  {c_type}: {count} 条 ({percentage:.1f}%)")
        
        # 影响关系分布
        relationships = {}
        for q in questions:
            rel = q['causal_scenario']['relationship']
            relationships[rel] = relationships.get(rel, 0) + 1
        
        print(f"\n影响关系分布:")
        for rel, count in relationships.items():
            percentage = count / len(questions) * 100
            print(f"  {rel}: {count} 条 ({percentage:.1f}%)")
        
        # 性能指标分布
        performance_indicators = {}
        for q in questions:
            indicator = q['causal_scenario']['effect']
            performance_indicators[indicator] = performance_indicators.get(indicator, 0) + 1
        
        print(f"\n性能指标分布:")
        for indicator, count in performance_indicators.items():
            percentage = count / len(questions) * 100
            print(f"  {indicator}: {count} 条 ({percentage:.1f}%)")
        
        # 复杂度分布
        complexity_levels = {}
        for q in questions:
            complexity = q['metadata']['causal_complexity']
            complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
        
        print(f"\n问题复杂度分布:")
        for level, count in complexity_levels.items():
            percentage = count / len(questions) * 100
            print(f"  {level}: {count} 条 ({percentage:.1f}%)")
        
        print(f"\n总耗时: {total_time/60:.1f} 分钟")
        print(f"平均速度: {len(questions)/total_time*60:.1f} 条/分钟")
        
        print("\n=== 生成完成 ===")
        
    except KeyboardInterrupt:
        print("\n\n用户中断生成过程")
        if progress_bar:
            progress_bar.close()
        sys.exit(0)
    
    except Exception as e:
        print(f"\n生成过程中发生错误: {str(e)}")
        if progress_bar:
            progress_bar.close()
        sys.exit(1)


if __name__ == "__main__":
    main()