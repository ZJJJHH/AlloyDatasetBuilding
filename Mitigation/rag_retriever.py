#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG检索器 - 专门为失效诊断问题优化的检索模块
"""

import json
import os
import re
import random
from typing import List, Dict, Any
from collections import defaultdict


class RAGRetriever:
    """基于JSONL文件的失效诊断专用RAG检索器"""
    
    def __init__(self, jsonl_path: str):
        self.jsonl_path = jsonl_path
        self.data = []
        self.index = defaultdict(list)
        self.failure_index = defaultdict(list)
        
        # 预定义的失效相关关键词
        self.failure_keywords = [
            "应力腐蚀", "疲劳", "蠕变", "氢脆", "腐蚀", "磨损", 
            "冲击", "热疲劳", "断裂", "裂纹", "失效", "破坏"
        ]
        
        # 预定义的应用场景关键词
        self.application_keywords = [
            "航空航天", "生物医学", "化工", "海洋", "汽车", 
            "核电站", "体育器材", "军工", "能源", "电子"
        ]
        
        # 加载数据
        self._load_data()
        self._build_index()
        self._build_failure_index()
        
        print(f"失效诊断RAG检索器初始化完成，共加载 {len(self.data)} 条合金数据")
    
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
    
    def _build_failure_index(self):
        """构建失效相关索引"""
        for record in self.data:
            # 检查性能数据中的失效相关指标
            performance_data = record.get('performance_data', {})
            
            # 提取与失效相关的性能参数
            failure_related_props = self._extract_failure_related_properties(performance_data)
            
            # 根据性能参数建立失效类型索引
            for prop_name, value in performance_data.items():
                if value and str(value).strip() and value != '':
                    # 检查是否与失效相关
                    failure_types = self._identify_failure_types(prop_name)
                    for f_type in failure_types:
                        self.failure_index[f_type].append(record)
    
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
        
        for term in self.application_keywords:
            if term in text:
                keywords.append(term)
        
        return keywords if keywords else ['通用应用']
    
    def _extract_failure_related_properties(self, performance_data: Dict) -> List[str]:
        """提取与失效相关的性能参数"""
        failure_props = []
        
        # 失效相关性能参数映射
        failure_property_mapping = {
            "疲劳性能": ["疲劳", "寿命", "循环", "S-N"],
            "腐蚀性能": ["腐蚀", "耐蚀", "电化学", "极化"],
            "蠕变性能": ["蠕变", "持久", "高温"],
            "冲击性能": ["冲击", "韧性", "夏比"],
            "断裂性能": ["断裂", "KIC", "韧性"],
            "硬度性能": ["硬度", "耐磨"]
        }
        
        for prop_name in performance_data.keys():
            if performance_data[prop_name]:
                for failure_type, keywords in failure_property_mapping.items():
                    for keyword in keywords:
                        if keyword in prop_name:
                            failure_props.append(failure_type)
                            break
        
        return list(set(failure_props))  # 去重
    
    def _identify_failure_types(self, prop_name: str) -> List[str]:
        """识别失效类型"""
        failure_types = []
        
        # 失效类型与性能参数关联
        failure_mapping = {
            "应力腐蚀开裂": ["腐蚀", "应力", "SCC"],
            "疲劳断裂": ["疲劳", "寿命", "循环"],
            "高温蠕变失效": ["蠕变", "持久", "高温"],
            "氢脆": ["氢", "脆性", "延迟"],
            "腐蚀失效": ["腐蚀", "耐蚀", "电化学"],
            "磨损失效": ["磨损", "硬度", "耐磨"],
            "冲击破坏": ["冲击", "韧性", "夏比"],
            "热疲劳": ["热疲劳", "热循环", "热应力"]
        }
        
        for failure_type, keywords in failure_mapping.items():
            for keyword in keywords:
                if keyword in prop_name:
                    failure_types.append(failure_type)
                    break
        
        return failure_types if failure_types else ['其他失效']
    
    def retrieve_by_failure_type(self, failure_type: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        根据失效类型检索相关合金数据
        
        Args:
            failure_type: 失效类型
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相关合金数据列表
        """
        if failure_type in self.failure_index:
            records = self.failure_index[failure_type]
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
        
        # 应用领域
        app_keywords = self._extract_application_keywords(query)
        keywords.extend(app_keywords)
        
        # 失效类型
        for failure_keyword in self.failure_keywords:
            if failure_keyword in query:
                keywords.append(failure_keyword)
        
        # 诊断相关关键词
        diagnosis_terms = ['分析', '诊断', '检测', '原因', '措施', '修复', '预防']
        for term in diagnosis_terms:
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
        
        # 检查应用领域匹配
        application = record.get('application_info', {}).get('应用领域', '').lower()
        for keyword in query_keywords:
            if keyword.lower() in application:
                score += 1.5
        
        # 检查失效相关性能匹配
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
            'application_fields': defaultdict(int),
            'failure_types': defaultdict(int)
        }
        
        for record in self.data:
            # 统计合金类型
            composition = record.get('material_info', {}).get('合金成分', '')
            alloy_codes = self._extract_alloy_codes(composition)
            for code in alloy_codes:
                stats['alloy_types'][code] += 1
            
            # 统计应用领域
            application = record.get('application_info', {}).get('应用领域', '')
            app_keywords = self._extract_application_keywords(application)
            for keyword in app_keywords:
                stats['application_fields'][keyword] += 1
            
            # 统计失效类型
            performance_data = record.get('performance_data', {})
            for prop_name in performance_data.keys():
                if performance_data[prop_name]:
                    failure_types = self._identify_failure_types(prop_name)
                    for f_type in failure_types:
                        stats['failure_types'][f_type] += 1
        
        return stats


# 测试函数
if __name__ == "__main__":
    # 测试检索器
    retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
    
    # 测试按失效类型检索
    results = retriever.retrieve_by_failure_type("疲劳断裂", k=3)
    print(f"按疲劳断裂检索到 {len(results)} 条结果")
    
    # 显示统计信息
    stats = retriever.get_statistics()
    print("\n数据统计:")
    print(f"总记录数: {stats['total_records']}")
    print("合金类型分布:", dict(stats['alloy_types']))
    print("应用领域分布:", dict(stats['application_fields']))
    print("失效类型分布:", dict(stats['failure_types']))