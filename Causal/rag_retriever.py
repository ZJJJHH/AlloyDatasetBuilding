#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG检索器 - 专门为因果关系分析问题优化的检索模块
"""

import json
import os
import re
import random
from typing import List, Dict, Any
from collections import defaultdict


class RAGRetriever:
    """基于JSONL文件的因果关系专用RAG检索器"""
    
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.data = []
        self.index = defaultdict(list)
        self.element_index = defaultdict(list)
        self.process_index = defaultdict(list)
        
        # 预定义的合金元素
        self.alloy_elements = [
            "Al", "V", "Sn", "Zr", "Mo", "Nb", "Ta", "Fe", 
            "Cr", "Ni", "Cu", "Si", "O", "N", "H", "C"
        ]
        
        # 预定义的工艺参数
        self.process_parameters = [
            "固溶处理", "时效处理", "冷却速率", "变形量", 
            "变形温度", "热处理时间", "退火温度", "淬火"
        ]
        
        # 预定义的性能指标
        self.performance_indicators = [
            "强度", "塑性", "韧性", "硬度", "疲劳", 
            "蠕变", "腐蚀", "断裂韧性", "热稳定性"
        ]
        
        # 加载数据
        self._load_data()
        self._build_index()
        self._build_element_index()
        self._build_process_index()
        
        print(f"因果关系RAG检索器初始化完成，共加载 {len(self.data)} 条合金数据")
    
    def _load_data(self):
        """加载JSONL数据"""
        if not os.path.exists(self.jsonl_path):
            raise FileNotFoundError(f"JSONL文件不存在: {self.jsonl_path}")
        
        with open(self.jsonl_path, 'r', encoding='utf-8-sig') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    if line.strip():
                        record = json.loads(line.strip())
                        # 为每条记录添加唯一ID
                        record['id'] = f"alloy_{line_num:06d}"
                        self.data.append(record)
                except json.JSONDecodeError as e:
                    print(f"警告：第 {line_num} 行JSON解析错误: {e}")
                    continue
    
    def _build_index(self):
        """构建关键词索引"""
        for record in self.data:
            # 提取合金成分关键词
            composition = record.get('material_info', {}).get('合金成分', '')
            if composition:
                # 提取合金牌号
                alloy_codes = self._extract_alloy_codes(composition)
                for code in alloy_codes:
                    self.index[code.lower()].append(record)
            
            # 提取应用领域关键词
            application = record.get('application_info', {}).get('应用领域', '')
            if application:
                app_keywords = self._extract_application_keywords(application)
                for keyword in app_keywords:
                    self.index[keyword.lower()].append(record)
    
    def _build_element_index(self):
        """构建元素索引"""
        for record in self.data:
            composition = record.get('material_info', {}).get('合金成分', '')
            if composition:
                # 提取合金中的元素
                elements = self._extract_elements_from_composition(composition)
                for element in elements:
                    self.element_index[element].append(record)
    
    def _build_process_index(self):
        """构建工艺参数索引"""
        for record in self.data:
            # 检查工艺信息
            process_info = record.get('process_info', {})
            
            # 检查性能数据中的工艺相关指标
            performance_data = record.get('performance_data', {})
            
            # 提取工艺参数
            process_params = self._extract_process_parameters(process_info, performance_data)
            for param in process_params:
                self.process_index[param].append(record)
    
    def _extract_alloy_codes(self, composition: str) -> List[str]:
        """提取合金牌号"""
        codes = []
        
        # 常见钛合金牌号模式
        patterns = [
            r'TC[1-9]\d*',  # TC系列
            r'Ti-\d+[A-Za-z]+-\d+[A-Za-z]*',  # Ti-Al-V等
            r'TA[1-9]\d*',  # TA系列
            r'TB[1-9]\d*',  # TB系列
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, composition)
            codes.extend(matches)
        
        # 如果没有匹配到标准牌号，使用成分描述
        if not codes:
            # 提取主要元素
            elements = re.findall(r'[A-Z][a-z]?\d*\.?\d*', composition)
            if elements:
                codes.append('_'.join(elements[:3]))  # 取前三个主要元素
        
        return codes if codes else ['unknown_alloy']
    
    def _extract_application_keywords(self, text: str) -> List[str]:
        """提取应用领域关键词"""
        if not text:
            return []
        
        keywords = []
        
        # 常见应用领域
        application_fields = [
            "航空航天", "生物医学", "化工", "海洋", "汽车", 
            "核电站", "体育器材", "军工", "能源", "电子"
        ]
        
        for field in application_fields:
            if field in text:
                keywords.append(field)
        
        return keywords if keywords else ['通用应用']
    
    def _extract_elements_from_composition(self, composition: str) -> List[str]:
        """从合金成分中提取元素"""
        elements = []
        
        for element in self.alloy_elements:
            if element in composition:
                elements.append(element)
        
        return elements if elements else ['Al', 'V']  # 默认返回常见元素
    
    def _extract_process_parameters(self, process_info: Dict, performance_data: Dict) -> List[str]:
        """提取工艺参数"""
        params = []
        
        # 从工艺信息中提取
        for key, value in process_info.items():
            if value and str(value).strip() and value != '':
                for param in self.process_parameters:
                    if param in key:
                        params.append(param)
        
        # 从性能数据中推断工艺参数
        for prop_name in performance_data.keys():
            if performance_data[prop_name]:
                # 检查是否与特定工艺相关
                if "热处理" in prop_name or "处理" in prop_name:
                    params.append("热处理")
                elif "变形" in prop_name:
                    params.append("变形工艺")
                elif "冷却" in prop_name:
                    params.append("冷却工艺")
        
        return list(set(params))  # 去重
    
    def retrieve_by_element(self, element: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        根据元素检索相关合金数据
        
        Args:
            element: 合金元素
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if element in self.element_index:
            records = self.element_index[element]
            return random.sample(records, min(k, len(records)))
        else:
            return []
    
    def retrieve_by_process(self, process_param: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        根据工艺参数检索相关合金数据
        
        Args:
            process_param: 工艺参数
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if process_param in self.process_index:
            records = self.process_index[process_param]
            return random.sample(records, min(k, len(records)))
        else:
            return []
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        基于查询检索相关合金数据
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if not self.data:
            return []
        
        # 提取查询关键词
        query_keywords = self._extract_query_keywords(query)
        
        # 计算相关性得分
        scored_results = []
        
        for record in self.data:
            score = self._calculate_relevance_score(record, query_keywords)
            if score > 0:
                scored_results.append((score, record))
        
        # 按得分排序并返回前k个
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # 如果结果不足k个，随机补充
        if len(scored_results) < k:
            results = [record for _, record in scored_results]
            remaining = k - len(results)
            if remaining > 0:
                random_records = random.sample(self.data, min(remaining, len(self.data)))
                results.extend(random_records)
            return results
        else:
            return [record for _, record in scored_results[:k]]
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        keywords = []
        
        # 合金牌号
        alloy_codes = self._extract_alloy_codes(query)
        keywords.extend(alloy_codes)
        
        # 合金元素
        for element in self.alloy_elements:
            if element in query:
                keywords.append(element)
        
        # 工艺参数
        for param in self.process_parameters:
            if param in query:
                keywords.append(param)
        
        # 性能指标
        for indicator in self.performance_indicators:
            if indicator in query:
                keywords.append(indicator)
        
        # 因果关系关键词
        causal_terms = ['影响', '导致', '引起', '促进', '抑制', '提高', '降低']
        for term in causal_terms:
            if term in query:
                keywords.append(term)
        
        return list(set(keywords))  # 去重
    
    def _calculate_relevance_score(self, record: Dict, query_keywords: List[str]) -> float:
        """计算相关性得分"""
        if not query_keywords:
            return 0.0
        
        score = 0.0
        
        # 检查合金成分匹配
        composition = record.get('material_info', {}).get('合金成分', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in composition:
                score += 2.0
        
        # 检查工艺信息匹配
        process_info = record.get('process_info', {})
        for key, value in process_info.items():
            if value:
                key_lower = key.lower()
                for keyword in query_keywords:
                    if keyword.lower() in key_lower:
                        score += 1.5
        
        # 检查性能数据匹配
        performance_data = record.get('performance_data', {})
        for prop_name, value in performance_data.items():
            if value:
                prop_name_lower = prop_name.lower()
                for keyword in query_keywords:
                    if keyword.lower() in prop_name_lower:
                        score += 1.0
        
        # 检查嵌入文本匹配
        embedding_text = record.get('embeddings', {}).get('text_for_embedding', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in embedding_text:
                score += 0.5
        
        return score
    
    def get_random_records(self, count: int = 1) -> List[Dict[str, Any]]:
        """随机获取合金记录"""
        if count >= len(self.data):
            return self.data.copy()
        else:
            return random.sample(self.data, count)
    
    def get_record_by_id(self, record_id: str) -> Dict[str, Any]:
        """根据ID获取记录"""
        for record in self.data:
            if record.get('id') == record_id:
                return record
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        stats = {
            'total_records': len(self.data),
            'alloy_types': defaultdict(int),
            'elements_present': defaultdict(int),
            'process_parameters': defaultdict(int),
            'performance_indicators': defaultdict(int)
        }
        
        for record in self.data:
            # 统计合金类型
            composition = record.get('material_info', {}).get('合金成分', '')
            alloy_codes = self._extract_alloy_codes(composition)
            for code in alloy_codes:
                stats['alloy_types'][code] += 1
            
            # 统计元素分布
            elements = self._extract_elements_from_composition(composition)
            for element in elements:
                stats['elements_present'][element] += 1
            
            # 统计工艺参数
            process_info = record.get('process_info', {})
            performance_data = record.get('performance_data', {})
            process_params = self._extract_process_parameters(process_info, performance_data)
            for param in process_params:
                stats['process_parameters'][param] += 1
            
            # 统计性能指标
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    for indicator in self.performance_indicators:
                        if indicator in prop_name:
                            stats['performance_indicators'][indicator] += 1
        
        return stats


# 测试函数
if __name__ == "__main__":
    # 测试检索器
    retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
    
    # 测试按元素检索
    results = retriever.retrieve_by_element("Al", k=3)
    print(f"按Al元素检索到 {len(results)} 条结果")
    
    # 测试按工艺检索
    results = retriever.retrieve_by_process("热处理", k=3)
    print(f"按热处理工艺检索到 {len(results)} 条结果")
    
    # 显示统计信息
    stats = retriever.get_statistics()
    print("\n数据统计:")
    print(f"总记录数: {stats['total_records']}")
    print("合金类型分布:", dict(stats['alloy_types']))
    print("元素分布:", dict(stats['elements_present']))
    print("工艺参数分布:", dict(stats['process_parameters']))
    print("性能指标分布:", dict(stats['performance_indicators']))