#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源加载器 - 从Ti_data.jsonl中加载合金数据
根据答案中的data_sources字段直接查询对应的数据条目
"""

import json
import os
import sys
from typing import Dict, List, Optional


class DataSourceLoader:
    """数据源加载器"""
    
    def __init__(self, data_path: str):
        """
        初始化数据源加载器
        
        Args:
            data_path: Ti_data.jsonl文件路径
        """
        self.data_path = data_path
        self.data = {}
        self._load_data()
    
    def _load_data(self):
        """从Ti_data.jsonl加载数据"""
        if not os.path.exists(self.data_path):
            print(f"警告：数据文件不存在: {self.data_path}")
            return
        
        try:
            with open(self.data_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line.strip())
                            alloy_id = record.get('id', '')
                            if alloy_id:
                                self.data[alloy_id] = record
                        except json.JSONDecodeError as e:
                            print(f"警告：解析JSON失败: {e}")
                            continue
        except UnicodeDecodeError:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line.strip())
                            alloy_id = record.get('id', '')
                            if alloy_id:
                                self.data[alloy_id] = record
                        except json.JSONDecodeError as e:
                            print(f"警告：解析JSON失败: {e}")
                            continue
        
        print(f"数据源加载完成，共加载 {len(self.data)} 条数据")
    
    def get_alloy_info(self, alloy_id: str) -> Optional[Dict]:
        """
        获取单个合金的信息
        
        Args:
            alloy_id: 合金ID（如 "alloy_000001"）
        
        Returns:
            合金信息字典，如果不存在则返回None
        """
        # 处理不同的ID格式
        if alloy_id in self.data:
            return self.data[alloy_id]
        
        # 尝试不同的ID格式
        # 例如 alloy_000001 -> 0000d1e127a570f76adcf7ef82fbb7fc5bda36b58fd45529f21f6c3ccb1a8cd1_0.0
        # 这里需要根据实际的ID格式进行映射
        return None
    
    def get_alloy_infos(self, alloy_ids: List[str]) -> List[Dict]:
        """
        获取多个合金的信息
        
        Args:
            alloy_ids: 合金ID列表
        
        Returns:
            合金信息列表
        """
        results = []
        for alloy_id in alloy_ids:
            info = self.get_alloy_info(alloy_id)
            if info:
                results.append(info)
        
        return results
    
    def format_alloy_info_for_scoring(self, alloy_info: Dict) -> str:
        """
        格式化合金信息为评分可用的文本
        
        Args:
            alloy_info: 合金信息字典
        
        Returns:
            格式化后的文本
        """
        if not alloy_info:
            return "无合金信息"
        
        lines = []
        
        # 合金成分
        material_info = alloy_info.get('material_info', {})
        alloy_composition = material_info.get('合金成分', '未知')
        lines.append(f"合金成分: {alloy_composition}")
        
        # 材料状态
        material_state = material_info.get('材料状态', '未知')
        if material_state:
            lines.append(f"材料状态: {material_state}")
        
        # 性能数据
        performance_data = alloy_info.get('performance_data', {})
        if performance_data:
            lines.append("性能数据:")
            for key, value in performance_data.items():
                lines.append(f"  - {key}: {value}")
        
        # 元素组成
        elemental_composition = alloy_info.get('elemental_composition', {})
        if elemental_composition:
            lines.append("元素组成:")
            for element, content in elemental_composition.items():
                lines.append(f"  - {element}: {content}%")
        
        # 论文信息
        metadata = alloy_info.get('metadata', {})
        paper_title = metadata.get('paper_title', '未知')
        if paper_title:
            lines.append(f"论文标题: {paper_title}")
        
        # 应用信息
        application_info = alloy_info.get('application_info', {})
        if application_info:
            lines.append("应用信息:")
            for key, value in application_info.items():
                lines.append(f"  - {key}: {value}")
        
        return '\n'.join(lines)
    
    def format_alloy_infos_for_scoring(self, alloy_ids: List[str]) -> str:
        """
        格式化多个合金信息为评分可用的文本
        
        Args:
            alloy_ids: 合金ID列表
        
        Returns:
            格式化后的文本
        """
        infos = self.get_alloy_infos(alloy_ids)
        
        if not infos:
            return "未找到相关合金数据"
        
        text = "相关合金数据源信息：\n\n"
        
        for i, info in enumerate(infos, 1):
            text += f"【数据源 {i}】\n"
            text += self.format_alloy_info_for_scoring(info)
            text += "\n\n"
        
        return text


if __name__ == "__main__":
    # 测试数据源加载器
    data_path = '/path/to/AlloyDatasetBuilding/Ti_data.jsonl'
    
    loader = DataSourceLoader(data_path)
    
    # 测试查询
    test_ids = ['alloy_000001', 'alloy_000002']
    infos = loader.get_alloy_infos(test_ids)
    
    print(f"查询到 {len(infos)} 条数据")
    
    for i, info in enumerate(infos, 1):
        print(f"\n数据源 {i}:")
        print(loader.format_alloy_info_for_scoring(info))
