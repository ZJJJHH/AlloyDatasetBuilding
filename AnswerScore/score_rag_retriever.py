#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分RAG检索器 - 为评分大模型提供相关合金数据
基于Ti_data.jsonl文件，专门用于评分时的数据检索
"""

import json
import os
import re
import random
from typing import List, Dict, Any
from collections import defaultdict


class ScoreRAGRetriever:
    """基于JSONL文件的评分专用RAG检索器"""
    
    def __init__(self, jsonl_path: str = '/path/to/AlloyDatasetBuilding/Ti_data.jsonl'):
        self.jsonl_path = jsonl_path
        self.data = []
        self.index = defaultdict(list)
        self.property_index = defaultdict(list)
        
        # 加载数据
        self._load_data()
        self._build_index()
        self._build_property_index()
        
        print(f"评分RAG检索器初始化完成，共加载 {len(self.data)} 条合金数据")
    
    def _load_data(self):
        """加载JSONL数据"""
        if not os.path.exists(self.jsonl_path):
            raise FileNotFoundError(f"JSONL文件不存在: {self.jsonl_path}")
        
        try:
            with open(self.jsonl_path, 'r', encoding='utf-8-sig') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            record = json.loads(line.strip())
                            # 为每条记录添加唯一ID（与Ti_data.jsonl中的id一致）
                            record['id'] = record.get('id', f"alloy_{line_num:06d}")
                            self.data.append(record)
                    except json.JSONDecodeError as e:
                        print(f"警告：第 {line_num} 行JSON解析错误: {e}")
                        continue
        except UnicodeDecodeError:
            with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            record = json.loads(line.strip())
                            record['id'] = record.get('id', f"alloy_{line_num:06d}")
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
                app_keywords = self._extract_keywords(application)
                for keyword in app_keywords:
                    self.index[keyword.lower()].append(record)
    
    def _build_property_index(self):
        """构建性能参数索引"""
        for record in self.data:
            performance_data = record.get('performance_data', {})
            
            for prop_name, value in performance_data.items():
                if value and str(value).strip() and value != '':
                    # 提取性能类型
                    prop_type = self._extract_property_type(prop_name)
                    if prop_type:
                        self.property_index[prop_type].append(record)
    
    def _extract_alloy_codes(self, composition: str) -> List[str]:
        """提取合金牌号"""
        codes = []
        
        # 常见钛合金牌号模式
        patterns = [
            r'TC[1-9]\d*',  # TC系列
            r'Ti-\d+[A-Za-z]+-\d+[A-Za-z]*',  # Ti-Al-V等
            r'TA[1-9]\d*',  # TA系列
            r'TB[1-9]\d*',  # TB系列
            r'Ti-6Al-4V',  # Ti-6Al-4V
            r'Ti-5Al-5Mo',  # Ti-5Al-5Mo等
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
    
    def _extract_property_type(self, prop_name: str) -> str:
        """提取性能类型"""
        # 性能类型映射
        property_types = {
            '拉伸性能': ['拉伸', '抗拉', '屈服', '延伸率', '断后'],
            '疲劳性能': ['疲劳', '循环', '寿命', 'S-N曲线'],
            '腐蚀性能': ['腐蚀', '耐蚀', '电化学', '极化曲线'],
            '冲击性能': ['冲击', '韧性', '夏比', '缺口'],
            '蠕变性能': ['蠕变', '持久', '高温持久'],
            '硬度性能': ['硬度', '显微', '洛氏', '维氏'],
            '物理性能': ['密度', '弹性', '热膨胀', '热导率', '比热容'],
            '剪切性能': ['剪切', '剪切强度'],
            '断裂性能': ['断裂韧性', 'KIC'],
            '应力腐蚀': ['应力腐蚀', '腐蚀疲劳']
        }
        
        for prop_type, terms in property_types.items():
            for term in terms:
                if term in prop_name:
                    return prop_type
        
        return '其他性能'
    
    def retrieve_by_scenario(self, scenario: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
        """
        根据评分场景检索相关合金数据
        
        Args:
            scenario: 评分场景信息，包含alloy_composition, property_category等
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if not self.data:
            return []
        
        # 构建查询文本
        query_parts = []
        
        # 合金牌号
        alloy_composition = scenario.get('alloy_composition', '')
        if alloy_composition:
            query_parts.append(alloy_composition)
        
        # 性能类别
        property_category = scenario.get('property_category', '')
        if property_category:
            query_parts.append(property_category)
        
        # 具体性能
        specific_property = scenario.get('specific_property', '')
        if specific_property:
            query_parts.append(specific_property)
        
        # 测试条件
        measurement_conditions = scenario.get('measurement_conditions', '')
        if measurement_conditions:
            query_parts.append(measurement_conditions)
        
        query = ' '.join(query_parts)
        
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
        
        # 应用领域
        app_keywords = self._extract_keywords(query)
        keywords.extend(app_keywords)
        
        # 性能类型
        property_types = ['拉伸', '疲劳', '腐蚀', '冲击', '蠕变', '硬度', '物理', '剪切', '断裂']
        for prop_type in property_types:
            if prop_type in query:
                keywords.append(prop_type)
        
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
        
        # 检查应用领域匹配
        application = record.get('application_info', {}).get('应用领域', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in application:
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
    
    def format_retrieved_data_for_scoring(self, records: List[Dict[str, Any]]) -> str:
        """
        格式化检索到的数据为评分可用的文本
        
        Args:
            records: 检索到的合金数据列表
            
        Returns:
            格式化后的文本
        """
        if not records:
            return "未找到相关合金数据"
        
        text = "相关合金数据源信息：\n\n"
        
        for i, record in enumerate(records, 1):
            text += f"【数据源 {i}】\n"
            text += self._format_record_for_scoring(record)
            text += "\n\n"
        
        return text
    
    def _format_record_for_scoring(self, record: Dict[str, Any]) -> str:
        """
        格式化单条记录为评分可用的文本
        
        Args:
            record: 合金数据记录
            
        Returns:
            格式化后的文本
        """
        lines = []
        
        # 合金成分
        material_info = record.get('material_info', {})
        alloy_composition = material_info.get('合金成分', '未知')
        lines.append(f"合金成分: {alloy_composition}")
        
        # 材料状态
        material_state = material_info.get('材料状态', '未知')
        if material_state:
            lines.append(f"材料状态: {material_state}")
        
        # 性能数据
        performance_data = record.get('performance_data', {})
        if performance_data:
            lines.append("性能数据:")
            for key, value in performance_data.items():
                lines.append(f"  - {key}: {value}")
        
        # 元素组成
        elemental_composition = record.get('elemental_composition', {})
        if elemental_composition:
            lines.append("元素组成:")
            for element, content in elemental_composition.items():
                lines.append(f"  - {element}: {content}%")
        
        # 论文信息
        metadata = record.get('metadata', {})
        paper_title = metadata.get('paper_title', '未知')
        if paper_title:
            lines.append(f"论文标题: {paper_title}")
        
        # 应用信息
        application_info = record.get('application_info', {})
        if application_info:
            lines.append("应用信息:")
            for key, value in application_info.items():
                lines.append(f"  - {key}: {value}")
        
        return '\n'.join(lines)
    
    def retrieve_and_format(self, scenario: Dict[str, Any], k: int = 3) -> str:
        """
        检索并格式化相关合金数据
        
        Args:
            scenario: 评分场景信息
            k: 返回结果数量
            
        Returns:
            格式化后的文本
        """
        records = self.retrieve_by_scenario(scenario, k)
        return self.format_retrieved_data_for_scoring(records)


if __name__ == "__main__":
    # 测试评分RAG检索器
    retriever = ScoreRAGRetriever()
    
    # 测试场景
    test_scenario = {
        'alloy_composition': 'Ti-6Al-4V (wt.%)',
        'property_category': '冲击性能',
        'specific_property': '性能参数范围',
        'measurement_conditions': '低温条件'
    }
    
    print("测试检索功能：")
    print("=" * 50)
    
    results = retriever.retrieve_by_scenario(test_scenario, k=3)
    
    print(f"检索到 {len(results)} 条相关数据：")
    for i, record in enumerate(results, 1):
        print(f"\n数据源 {i}:")
        print(retriever._format_record_for_scoring(record))
    
    print("\n" + "=" * 50)
    print("测试格式化功能：")
    print("=" * 50)
    
    formatted_text = retriever.retrieve_and_format(test_scenario, k=3)
    print(formatted_text)
