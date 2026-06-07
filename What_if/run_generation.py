#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反事实问题生成启动脚本
支持配置文件和命令行参数
"""

import json
import os
import sys
import argparse
import time
from generate_what_if_questions import WhatIfQuestionGenerator, save_questions_to_json
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient, MockDeepSeekClient

# 进度条支持
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("提示：未安装tqdm库，将使用简单进度显示。安装命令：pip install tqdm")


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return {}


def setup_environment():
    """设置环境"""
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)


def create_progress_bar(total, desc="生成进度"):
    """创建进度条"""
    if TQDM_AVAILABLE:
        return tqdm(total=total, desc=desc, unit="条", ncols=100)
    else:
        return SimpleProgressBar(total, desc)


class SimpleProgressBar:
    """简单的进度条实现（当tqdm不可用时使用）"""
    
    def __init__(self, total, desc="生成进度"):
        self.total = total
        self.desc = desc
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        
    def update(self, n=1):
        """更新进度"""
        self.current += n
        current_time = time.time()
        
        # 每处理10条记录或每5秒更新一次显示
        if self.current % 10 == 0 or current_time - self.last_update >= 5:
            self._display()
            self.last_update = current_time
    
    def _display(self):
        """显示进度"""
        elapsed = time.time() - self.start_time
        percent = (self.current / self.total) * 100
        
        if self.current > 0:
            speed = self.current / elapsed
            eta = (self.total - self.current) / speed if speed > 0 else 0
            eta_str = f"预计剩余: {eta/60:.1f}分钟"
        else:
            speed = 0
            eta_str = "预计剩余: 计算中..."
        
        print(f"\r{self.desc}: {self.current}/{self.total} ({percent:.1f}%) | "
              f"速度: {speed*60:.1f}条/分钟 | {eta_str}", end="", flush=True)
    
    def close(self):
        """完成进度条"""
        self._display()
        print()  # 换行


def validate_config(config: dict) -> bool:
    """验证配置"""
    required_fields = [
        'generation_config.rag_data_path',
        'generation_config.output_path',
        'deepseek_config.api_key'
    ]
    
    for field in required_fields:
        keys = field.split('.')
        current = config
        for key in keys:
            if key not in current:
                print(f"配置错误: 缺少字段 {field}")
                return False
            current = current[key]
    
    # 检查数据文件是否存在
    rag_path = config['generation_config']['rag_data_path']
    if not os.path.exists(rag_path):
        print(f"错误: RAG数据文件不存在: {rag_path}")
        return False
    
    return True


def main():
    """主函数"""
    
    # 设置参数解析
    parser = argparse.ArgumentParser(description='反事实问题生成器')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    parser.add_argument('--count', type=int, help='生成问题数量')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--mock', action='store_true', help='使用模拟模式（不调用真实API）')
    parser.add_argument('--test', action='store_true', help='测试模式（生成少量问题）')
    
    args = parser.parse_args()
    
    # 设置环境
    setup_environment()
    
    print("=== 反事实问题生成器 ===")
    
    # 加载配置
    config = load_config(args.config)
    if not config:
        print("无法加载配置，使用默认配置")
        config = {
            "generation_config": {
                "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
                "output_path": "/path/to/AlloyDatasetBuilding/What_if/what_if_questions.json",
                "target_question_count": 1000
            },
            "deepseek_config": {
                "api_key": "YOUR_API_KEY_HERE"
            }
        }
    
    # 应用命令行参数覆盖
    if args.count:
        config['generation_config']['target_question_count'] = args.count
    if args.output:
        config['generation_config']['output_path'] = args.output
    
    # 测试模式：生成少量问题
    if args.test:
        config['generation_config']['target_question_count'] = 10
        print("测试模式：生成10个问题")
    
    # 验证配置
    if not validate_config(config):
        print("配置验证失败，请检查配置文件")
        sys.exit(1)
    
    # 初始化组件
    print("\n初始化组件...")
    
    # RAG检索器
    try:
        rag_retriever = RAGRetriever(config['generation_config']['rag_data_path'])
        print("✓ RAG检索器初始化成功")
    except Exception as e:
        print(f"✗ RAG检索器初始化失败: {str(e)}")
        sys.exit(1)
    
    # DeepSeek客户端
    if args.mock:
        deepseek_client = MockDeepSeekClient()
        print("✓ 模拟DeepSeek客户端初始化成功（测试模式）")
    else:
        api_key = config['deepseek_config']['api_key']
        if api_key == "YOUR_DEEPSEEK_API_KEY_HERE" or not api_key:
            print("✗ 请配置有效的DeepSeek API密钥")
            print("  请在config.json中设置deepseek_config.api_key")
            print("  或使用 --mock 参数进行测试")
            sys.exit(1)
        
        try:
            deepseek_client = DeepSeekClient(api_key)
            
            # 验证API密钥
            if not deepseek_client.validate_api_key():
                print("✗ API密钥验证失败")
                sys.exit(1)
            
            print("✓ DeepSeek客户端初始化成功")
        except Exception as e:
            print(f"✗ DeepSeek客户端初始化失败: {str(e)}")
            sys.exit(1)
    
    # 问题生成器
    generator = WhatIfQuestionGenerator(rag_retriever, deepseek_client)
    print("✓ 问题生成器初始化成功")
    
    # 生成问题
    target_count = config['generation_config']['target_question_count']
    output_path = config['generation_config']['output_path']
    
    print(f"\n开始生成 {target_count} 个反事实问题...")
    
    # 创建进度条
    progress_bar = create_progress_bar(target_count, "反事实问题生成进度")
    
    # 使用进度条生成问题
    questions = generator.generate_batch_questions(target_count, progress_bar)
    
    # 关闭进度条
    progress_bar.close()
    
    # 保存结果
    if questions:
        save_questions_to_json(questions, output_path)
        
        # 显示统计信息
        print("\n=== 生成统计 ===")
        print(f"总问题数: {len(questions)}")
        
        # API调用统计
        api_stats = deepseek_client.get_statistics()
        print("API调用统计:")
        for key, value in api_stats.items():
            print(f"  {key}: {value}")
        
        # 问题类型分布
        alloy_types = {}
        for q in questions:
            alloy = q['reference_alloy']['composition']
            if 'TC4' in alloy or 'Ti-6Al-4V' in alloy:
                alloy_types['TC4'] = alloy_types.get('TC4', 0) + 1
            elif 'Ti-5Al-2.5Sn' in alloy:
                alloy_types['Ti-5Al-2.5Sn'] = alloy_types.get('Ti-5Al-2.5Sn', 0) + 1
            else:
                alloy_types['其他'] = alloy_types.get('其他', 0) + 1
        
        print("\n合金类型分布:")
        for alloy_type, count in alloy_types.items():
            percentage = count / len(questions) * 100
            print(f"  {alloy_type}: {count} 条 ({percentage:.1f}%)")
    
    else:
        print("生成失败，没有生成任何问题")
    
    print("=== 生成完成 ===")


if __name__ == "__main__":
    main()