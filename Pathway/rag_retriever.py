#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG检索器 - 专门为微观组织机制解释问题优化的检索模块
"""

import json
import os
import re
import random
from typing import List, Dict, Any
from collections import defaultdict


class RAGRetriever:
    """基于JSONL文件的机制解释专用RAG检索器"""
    
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.data = []
        self.index = defaultdict(list)
        self.microstructure_index = defaultdict(list)
        self.mechanism_index = defaultdict(list)
        
        # 预定义的微观组织特征
        self.microstructural_features = [
            "α相", "β相", "α+β双相组织", "晶粒尺寸", "晶界特征",
            "析出相", "孪晶", "位错密度", "相界面", "织构"
        ]
        
        # 预定义的工艺过程
        self.process_pathways = [
            "热处理过程", "变形过程", "冷却过程", "时效过程",
            "相变过程", "再结晶过程", "晶粒长大过程"
        ]
        
        # 预定义的影响机制
        self.mechanisms = [
            "固溶强化", "析出强化", "细晶强化", "位错强化",
            "相变强化", "织构强化", "界面强化"
        ]
        
        # 预定义的宏观性能
        self.macro_properties = [
            "强度", "塑性", "韧性", "硬度", "疲劳", 
            "蠕变", "腐蚀", "断裂韧性", "热稳定性"
        ]
        
        # 加载数据
        self._load_data()
        self._build_index()
        self._build_microstructure_index()
        self._build_mechanism_index()
        
        print(f"机制解释RAG检索器初始化完成，共加载 {len(self.data)} 条合金数据")
    
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
    
    def _build_microstructure_index(self):
        """构建微观组织索引"""
        for record in self.data:
            # 检查微观组织信息
            microstructure_info = record.get('microstructure_info', {})
            
            # 检查性能数据中的微观组织相关指标
            performance_data = record.get('performance_data', {})
            
            # 提取微观组织特征
            micro_features = self._extract_microstructural_features(microstructure_info, performance_data)
            for feature in micro_features:
                self.microstructure_index[feature].append(record)
    
    def _build_mechanism_index(self):
        """构建机制索引"""
        for record in self.data:
            # 检查工艺信息
            process_info = record.get('process_info', {})
            
            # 检查性能数据中的机制相关指标
            performance_data = record.get('performance_data', {})
            
            # 提取强化机制
            mechanisms = self._extract_mechanisms(process_info, performance_data)
            for mechanism in mechanisms:
                self.mechanism_index[mechanism].append(record)
    
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
    
    def _extract_microstructural_features(self, microstructure_info: Dict, performance_data: Dict) -> List[str]:
        """提取微观组织特征"""
        features = []
        
        # 从微观组织信息中提取
        for key, value in microstructure_info.items():
            if value and str(value).strip() and value != '':
                for feature in self.microstructural_features:
                    if feature in key:
                        features.append(feature)
        
        # 从性能数据中推断微观组织特征
        for prop_name in performance_data.keys():
            if performance_data[prop_name]:
                # 检查是否与特定微观组织相关
                if "α相" in prop_name or "α" in prop_name:
                    features.append("α相")
                elif "β相" in prop_name or "β" in prop_name:
                    features.append("β相")
                elif "晶粒" in prop_name:
                    features.append("晶粒尺寸")
                elif "析出" in prop_name:
                    features.append("析出相")
        
        return list(set(features))  # 去重
    
    def _extract_mechanisms(self, process_info: Dict, performance_data: Dict) -> List[str]:
        """提取强化机制"""
        mechanisms = []
        
        # 从工艺信息中提取
        for key, value in process_info.items():
            if value and str(value).strip() and value != '':
                for mechanism in self.mechanisms:
                    if mechanism in key:
                        mechanisms.append(mechanism)
        
        # 从性能数据中推断强化机制
        for prop_name in performance_data.keys():
            if performance_data[prop_name]:
                # 检查是否与特定机制相关
                if "固溶" in prop_name:
                    mechanisms.append("固溶强化")
                elif "析出" in prop_name:
                    mechanisms.append("析出强化")
                elif "细晶" in prop_name or "晶粒" in prop_name:
                    mechanisms.append("细晶强化")
                elif "位错" in prop_name:
                    mechanisms.append("位错强化")
        
        return list(set(mechanisms))  # 去重
    
    def retrieve_by_microstructure(self, micro_feature: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        根据微观组织特征检索相关合金数据
        
        Args:
            micro_feature: 微观组织特征
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if micro_feature in self.microstructure_index:
            records = self.microstructure_index[micro_feature]
            return random.sample(records, min(k, len(records)))
        else:
            return []
    
    def retrieve_by_mechanism(self, mechanism: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        根据强化机制检索相关合金数据
        
        Args:
            mechanism: 强化机制
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if mechanism in self.mechanism_index:
            records = self.mechanism_index[mechanism]
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
        
        # 微观组织特征
        for feature in self.microstructural_features:
            if feature in query:
                keywords.append(feature)
        
        # 工艺过程
        for process in self.process_pathways:
            if process in query:
                keywords.append(process)
        
        # 强化机制
        for mechanism in self.mechanisms:
            if mechanism in query:
                keywords.append(mechanism)
        
        # 宏观性能
        for property in self.macro_properties:
            if property in query:
                keywords.append(property)
        
        # 机制解释关键词
        pathway_terms = ['演变', '机制', '路径', '过程', '形成', '影响', '关联']
        for term in pathway_terms:
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
        
        # 检查微观组织信息匹配
        microstructure_info = record.get('microstructure_info', {})
        for key, value in microstructure_info.items():
            if value:
                key_lower = key.lower()
                for keyword in query_keywords:
                    if keyword.lower() in key_lower:
                        score += 1.5
        
        # 检查工艺信息匹配
        process_info = record.get('process_info', {})
        for key, value in process_info.items():
            if value:
                key_lower = key.lower()
                for keyword in query_keywords:
                    if keyword.lower() in key_lower:
                        score += 1.0
        
        # 检查性能数据匹配
        performance_data = record.get('performance_data', {})
        for prop_name, value in performance_data.items():
            if value:
                prop_name_lower = prop_name.lower()
                for keyword in query_keywords:
                    if keyword.lower() in prop_name_lower:
                        score += 0.5
        
        # 检查嵌入文本匹配
        embedding_text = record.get('embeddings', {}).get('text_for_embedding', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in embedding_text:
                score += 0.3
        
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
            'microstructural_features': defaultdict(int),
            'mechanisms': defaultdict(int),
            'process_pathways': defaultdict(int)
        }
        
        for record in self.data:
            # 统计合金类型
            composition = record.get('material_info', {}).get('合金成分', '')
            alloy_codes = self._extract_alloy_codes(composition)
            for code in alloy_codes:
                stats['alloy_types'][code] += 1
            
            # 统计微观组织特征
            microstructure_info = record.get('microstructure_info', {})
            performance_data = record.get('performance_data', {})
            micro_features = self._extract_microstructural_features(microstructure_info, performance_data)
            for feature in micro_features:
                stats['microstructural_features'][feature] += 1
            
            # 统计强化机制
            process_info = record.get('process_info', {})
            mechanisms = self._extract_mechanisms(process_info, performance_data)
            for mechanism in mechanisms:
                stats['mechanisms'][mechanism] += 1
            
            # 统计工艺过程
            for key in process_info.keys():
                if process_info[key]:
                    for pathway in self.process_pathways:
                        if pathway in key:
                            stats['process_pathways'][pathway] += 1
        
        return stats


# 测试函数
if __name__ == "__main__":
    # 测试检索器
    retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
    
    # 测试按微观组织检索
    results = retriever.retrieve_by_microstructure("α相", k=3)
    print(f"按α相检索到 {len(results)} 条结果")
    
    # 测试按机制检索
    results = retriever.retrieve_by_mechanism("析出强化", k=3)
    print(f"按析出强化机制检索到 {len(results)} 条结果")
    
    # 显示统计信息
    stats = retriever.get_statistics()
    print("\n数据统计:")
    print(f"总记录数: {stats['total_records']}")
    print("合金类型分布:", dict(stats['alloy_types']))
    print("微观组织特征分布:", dict(stats['microstructural_features']))
    print("强化机制分布:", dict(stats['mechanisms']))
    print("工艺过程分布:", dict(stats['process_pathways']))