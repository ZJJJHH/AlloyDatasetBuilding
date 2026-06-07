#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG检索器 - 基于语义深度匹配的检索模块
支持针对不同问题类型的专业化检索
"""

import json
import os
import re
import random
from typing import List, Dict, Any
from collections import defaultdict


class RAGRetriever:
    """基于JSONL文件的语义RAG检索器"""
    
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
                        record['id'] = f"alloy_{line_num:06d}"
                        self.data.append(record)
                except json.JSONDecodeError as e:
                    print(f"警告：第 {line_num} 行JSON解析错误: {e}")
                    continue
    
    def _build_index(self):
        """构建多维度索引"""
        for record in self.data:
            # 成分索引
            composition = record.get('material_info', {}).get('合金成分', '')
            if composition:
                alloy_codes = self._extract_alloy_codes(composition)
                for code in alloy_codes:
                    self.index[code.lower()].append(record)
            
            # 应用领域索引
            application = record.get('application_info', {}).get('应用领域', '')
            if application:
                app_keywords = self._extract_keywords(application)
                for keyword in app_keywords:
                    self.index[keyword.lower()].append(record)
            
            # 性能数据索引
            performance_data = record.get('performance_data', {})
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    perf_keywords = self._extract_performance_keywords(prop_name)
                    for keyword in perf_keywords:
                        self.index[keyword.lower()].append(record)
            
            # 嵌入文本索引（用于语义匹配）
            embedding_text = record.get('embeddings', {}).get('text_for_embedding', '')
            if embedding_text:
                embedding_keywords = self._extract_embedding_keywords(embedding_text)
                for keyword in embedding_keywords:
                    self.index[keyword.lower()].append(record)
    
    def _extract_alloy_codes(self, composition: str) -> List[str]:
        """提取合金牌号"""
        codes = []
        patterns = [
            r'TC[1-9]\d*',
            r'Ti-\d+[A-Za-z]+-\d+[A-Za-z]*',
            r'TA[1-9]\d*',
            r'TB[1-9]\d*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, composition)
            codes.extend(matches)
        
        if not codes:
            elements = re.findall(r'[A-Z][a-z]?\d*\.?\d*', composition)
            if elements:
                codes.append('_'.join(elements[:3]))
        
        return codes if codes else ['unknown_alloy']
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取应用领域关键词"""
        if not text:
            return []
        
        keywords = []
        application_terms = [
            '航空航天', '生物医学', '化工', '船舶', '汽车',
            '体育器材', '医疗器械', '军工', '能源', '电子',
            '微流体', '高温微流体', '轨道交通'
        ]
        
        for term in application_terms:
            if term in text:
                keywords.append(term)
        
        return keywords if keywords else ['通用应用']
    
    def _extract_performance_keywords(self, prop_name: str) -> List[str]:
        """提取性能关键词"""
        keywords = []
        performance_types = {
            '拉伸': ['拉伸', '抗拉', '屈服', '延伸率', '断后'],
            '疲劳': ['疲劳', '循环', '寿命', 'S-N曲线'],
            '腐蚀': ['腐蚀', '耐蚀', '电化学', '极化曲线'],
            '冲击': ['冲击', '韧性', '夏比', '缺口'],
            '蠕变': ['蠕变', '持久', '高温持久'],
            '硬度': ['硬度', '显微', '洛氏', '维氏'],
            '物理': ['密度', '弹性', '热膨胀', '热导率', '比热容'],
            '剪切': ['剪切', '剪切强度'],
            '断裂': ['断裂韧性', 'KIC']
        }
        
        for perf_type, terms in performance_types.items():
            for term in terms:
                if term in prop_name:
                    keywords.append(perf_type)
                    break
        
        return keywords if keywords else ['其他性能']
    
    def _extract_embedding_keywords(self, text: str) -> List[str]:
        """从嵌入文本中提取关键词"""
        keywords = []
        
        # 材料成分关键词
        element_terms = ['Al', 'V', 'Ti', 'Mo', 'Nb', 'Fe', 'Cr', 'Ni', 'Cu', 'Si', 'Zr', 'Sn']
        for term in element_terms:
            if term in text:
                keywords.append(term.lower())
        
        # 工艺关键词
        process_terms = ['热处理', '固溶', '时效', '退火', '淬火', '变形', '加工']
        for term in process_terms:
            if term in text:
                keywords.append(term)
        
        # 性能关键词
        property_terms = ['强度', '韧性', '塑性', '硬度', '疲劳', '蠕变', '腐蚀', '稳定性']
        for term in property_terms:
            if term in text:
                keywords.append(term)
        
        return list(set(keywords))
    
    def retrieve(self, query: str, question_type: str = None, k: int = 5) -> List[Dict[str, Any]]:
        """
        基于查询检索相关合金数据（支持问题类型特定的检索策略）
        
        Args:
            query: 查询文本（问题文本）
            question_type: 问题类型（用于定制化检索）
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if not self.data:
            return []
        
        # 提取查询关键词
        query_keywords = self._extract_query_keywords(query, question_type)
        
        # 计算相关性得分
        scored_results = []
        
        for record in self.data:
            score = self._calculate_relevance_score(record, query_keywords, question_type)
            if score > 0:
                scored_results.append((score, record))
        
        # 按得分排序
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前k个结果
        results = [record for _, record in scored_results[:k]]
        
        # 如果结果不足k个，随机补充
        if len(results) < k:
            remaining = k - len(results)
            available_records = [r for r in self.data if r not in results]
            if available_records:
                random_records = random.sample(available_records, min(remaining, len(available_records)))
                results.extend(random_records)
        
        return results[:k]
    
    def _extract_query_keywords(self, query: str, question_type: str = None) -> List[str]:
        """提取查询关键词（根据问题类型定制）"""
        keywords = []
        
        # 合金牌号
        alloy_codes = self._extract_alloy_codes(query)
        keywords.extend(alloy_codes)
        
        # 应用领域
        app_keywords = self._extract_keywords(query)
        keywords.extend(app_keywords)
        
        # 性能类型
        for prop_type in ['拉伸', '疲劳', '腐蚀', '冲击', '蠕变', '硬度', '物理', '剪切', '断裂']:
            if prop_type in query:
                keywords.append(prop_type)
        
        # 问题类型特定关键词
        
        if question_type == 'what_if':
            # 反事实问：关注设计、优化、调整相关词
            query_terms = ['设计', '优化', '调整', '改进', '方案', '策略', '如何', '目标']
            keywords.extend(query_terms)
        
        elif question_type == 'causal':
            # 因果问：关注影响、机制、原因相关词
            query_terms = ['影响', '机制', '原因', '是否', '导致', '协同', '作用']
            keywords.extend(query_terms)
        
        elif question_type == 'mitigation':
            # 失效诊断：关注失效、诊断、分析相关词
            query_terms = ['失效', '诊断', '分析', '原因', '措施', '修复', '预防']
            keywords.extend(query_terms)
        
        elif question_type == 'pathway':
            # 机制问：关注路径、演变、过程相关词
            query_terms = ['路径', '演变', '过程', '机制', '形成', '关联', '如何']
            keywords.extend(query_terms)
        
        return list(set(keywords))
    
    def _calculate_relevance_score(self, record: Dict, query_keywords: List[str], 
                                   question_type: str = None) -> float:
        """计算相关性得分（根据问题类型调整权重）"""
        if not query_keywords:
            return 0.0
        
        score = 0.0
        
        # 成分匹配（所有类型都重要）
        composition = record.get('material_info', {}).get('合金成分', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in composition:
                score += 3.0
        
        # 应用领域匹配
        application = record.get('application_info', {}).get('应用领域', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in application:
                score += 2.0
        
        # 性能数据匹配
        performance_data = record.get('performance_data', {})
        for prop_name, value in performance_data.items():
            if value:
                prop_name_lower = prop_name.lower()
                for keyword in query_keywords:
                    if keyword.lower() in prop_name_lower:
                        score += 1.5
        
        # 嵌入文本匹配（语义匹配）
        embedding_text = record.get('embeddings', {}).get('text_for_embedding', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in embedding_text:
                score += 1.0
        
        # 问题类型特定权重调整
        if question_type == 'what_if':
            # 反事实问：应用和成分匹配权重更高
            score += 1.0
        
        elif question_type == 'causal':
            # 因果问：性能和工艺信息匹配权重更高
            score += 1.0
        
        elif question_type == 'mitigation':
            # 失效诊断：失效相关关键词匹配权重更高
            if any(term in embedding_text for term in ['失效', '断裂', '腐蚀', '蠕变']):
                score += 2.0
        
        elif question_type == 'pathway':
            # 机制问：微观组织和工艺过程匹配权重更高
            if any(term in embedding_text for term in ['相变', '组织', '机制', '演变']):
                score += 2.0
        
        return score
    
    def retrieve_by_alloy(self, alloy_composition: str, k: int = 3) -> List[Dict[str, Any]]:
        """根据合金成分检索"""
        alloy_codes = self._extract_alloy_codes(alloy_composition)
        results = []
        
        for code in alloy_codes:
            if code.lower() in self.index:
                records = self.index[code.lower()]
                results.extend(records)
        
        return list(set(results))[:k]
    
    def retrieve_by_application(self, application: str, k: int = 3) -> List[Dict[str, Any]]:
        """根据应用领域检索"""
        keywords = self._extract_keywords(application)
        results = []
        
        for keyword in keywords:
            if keyword.lower() in self.index:
                records = self.index[keyword.lower()]
                results.extend(records)
        
        return list(set(results))[:k]
    
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
            composition = record.get('material_info', {}).get('合金成分', '')
            alloy_codes = self._extract_alloy_codes(composition)
            for code in alloy_codes:
                stats['alloy_types'][code] += 1
            
            application = record.get('application_info', {}).get('应用领域', '')
            app_keywords = self._extract_keywords(application)
            for keyword in app_keywords:
                stats['application_fields'][keyword] += 1
            
            performance_data = record.get('performance_data', {})
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    perf_keywords = self._extract_performance_keywords(prop_name)
                    for keyword in perf_keywords:
                        stats['performance_types'][keyword] += 1
        
        return stats


if __name__ == "__main__":
    # 测试检索器
    retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
    
    # 测试检索
    results = retriever.retrieve("TC4 高强度 航空航天", question_type="what_if", k=3)
    print(f"检索到 {len(results)} 条结果")
    
    # 显示统计信息
    stats = retriever.get_statistics()
    print(f"\n数据统计:")
    print(f"总记录数: {stats['total_records']}")
    print(f"合金类型数: {len(stats['alloy_types'])}")
