#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG检索器 - 基于钛合金JSONL数据集的检索模块
"""

import json
import os
import re
from typing import List, Dict, Any
from collections import defaultdict


class RAGRetriever:
    """基于JSONL文件的简单RAG检索器"""
    
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.data = []
        self.index = defaultdict(list)
        
        # 加载数据
        self._load_data()
        self._build_index()
        
        print(f"RAG检索器初始化完成，共加载 {len(self.data)} 条合金数据")
    
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
        """构建简单的关键词索引"""
        for record in self.data:
            # 提取合金成分关键词
            composition = record.get('material_info', {}).get('合金成分', '')
            if composition:
                # 提取合金牌号（如TC4, Ti-6Al-4V等）
                alloy_codes = self._extract_alloy_codes(composition)
                for code in alloy_codes:
                    self.index[code.lower()].append(record)
            
            # 提取应用领域关键词
            application = record.get('application_info', {}).get('应用领域', '')
            if application:
                # 分割应用领域
                app_keywords = self._extract_keywords(application)
                for keyword in app_keywords:
                    self.index[keyword.lower()].append(record)
            
            # 提取性能关键词
            performance_data = record.get('performance_data', {})
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    # 提取性能类型（如拉伸、疲劳、腐蚀等）
                    perf_keywords = self._extract_performance_keywords(prop_name)
                    for keyword in perf_keywords:
                        self.index[keyword.lower()].append(record)
    
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
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 中文分割（简单实现）
        keywords = []
        
        # 常见材料应用领域
        application_terms = [
            '航空航天', '生物医学', '化工', '船舶', '汽车', 
            '体育器材', '医疗器械', '军工', '能源', '电子'
        ]
        
        for term in application_terms:
            if term in text:
                keywords.append(term)
        
        return keywords if keywords else ['通用应用']
    
    def _extract_performance_keywords(self, prop_name: str) -> List[str]:
        """提取性能关键词"""
        keywords = []
        
        # 性能类型映射
        performance_types = {
            '拉伸': ['拉伸', '抗拉', '屈服', '延伸率'],
            '疲劳': ['疲劳', '循环', '寿命'],
            '腐蚀': ['腐蚀', '耐蚀', '电化学'],
            '冲击': ['冲击', '韧性', '夏比'],
            '蠕变': ['蠕变', '持久', '高温'],
            '硬度': ['硬度', '显微', '洛氏'],
            '物理': ['密度', '弹性', '热膨胀', '热导率']
        }
        
        for perf_type, terms in performance_types.items():
            for term in terms:
                if term in prop_name:
                    keywords.append(perf_type)
                    break
        
        return keywords if keywords else ['其他性能']
    
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
            # 返回所有相关结果
            results = [record for _, record in scored_results]
            # 随机补充剩余数量
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
        
        # 应用领域
        app_keywords = self._extract_keywords(query)
        keywords.extend(app_keywords)
        
        # 性能类型
        for prop_type in ['拉伸', '疲劳', '腐蚀', '冲击', '蠕变', '硬度', '物理']:
            if prop_type in query:
                keywords.append(prop_type)
        
        # 其他关键词
        other_terms = ['优化', '改进', '调整', '设计', '成本', '性能', '强度', '韧性']
        for term in other_terms:
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
                score += 2.0  # 成分匹配权重较高
        
        # 检查应用领域匹配
        application = record.get('application_info', {}).get('应用领域', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in application:
                score += 1.5
        
        # 检查性能数据匹配
        performance_data = record.get('performance_data', {})
        for prop_name, value in performance_data.items():
            if value:  # 只检查有数据的性能
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
        import random
        
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
            'application_fields': defaultdict(int),
            'performance_types': defaultdict(int)
        }
        
        for record in self.data:
            # 统计合金类型
            composition = record.get('material_info', {}).get('合金成分', '')
            alloy_codes = self._extract_alloy_codes(composition)
            for code in alloy_codes:
                stats['alloy_types'][code] += 1
            
            # 统计应用领域
            application = record.get('application_info', {}).get('应用领域', '')
            app_keywords = self._extract_keywords(application)
            for keyword in app_keywords:
                stats['application_fields'][keyword] += 1
            
            # 统计性能类型
            performance_data = record.get('performance_data', {})
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    perf_keywords = self._extract_performance_keywords(prop_name)
                    for keyword in perf_keywords:
                        stats['performance_types'][keyword] += 1
        
        return stats


# 测试函数
if __name__ == "__main__":
    # 测试检索器
    retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
    
    # 测试检索
    results = retriever.retrieve("TC4 高强度 航空航天", k=3)
    print(f"检索到 {len(results)} 条结果")
    
    # 显示统计信息
    stats = retriever.get_statistics()
    print("\n数据统计:")
    print(f"总记录数: {stats['total_records']}")
    print("合金类型分布:", dict(stats['alloy_types']))
    print("应用领域分布:", dict(stats['application_fields']))
    print("性能类型分布:", dict(stats['performance_types']))