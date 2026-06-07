#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本描述生成模块
用于将结构化的钛合金数据转换为自然语言描述，便于大模型理解和检索
"""

import re


def build_embedding_text(row):
    """
    构建用于向量化的完整文本描述
    
    Args:
        row: pandas Series，包含所有字段的数据
        
    Returns:
        str: 自然语言描述文本
    """
    
    # 基础信息
    text_parts = []
    
    # 论文标题
    if row.get('paper_title'):
        text_parts.append(f"研究论文《{row['paper_title']}》")
    
    # 合金信息
    alloy_info = []
    if row.get('合金成分'):
        alloy_info.append(f"{row['合金成分']}合金")
    if row.get('材料状态'):
        alloy_info.append(f"材料状态：{row['材料状态']}")
    
    if alloy_info:
        text_parts.append("针对" + "，".join(alloy_info))
    
    # 工艺信息
    process_info = []
    if row.get('制备工艺'):
        process_info.append(f"制备工艺：{row['制备工艺']}")
    if row.get('热处理工艺'):
        process_info.append(f"热处理工艺：{row['热处理工艺']}")
    if row.get('加工工艺'):
        process_info.append(f"加工工艺：{row['加工工艺']}")
    
    if process_info:
        text_parts.append("采用" + "、".join(process_info))
    
    # 性能数据（选择关键性能）
    performance = []
    
    # 拉伸性能
    if row.get('拉伸性能_屈服强度_工程应力（MPa）'):
        performance.append(f"屈服强度{row['拉伸性能_屈服强度_工程应力（MPa）']}MPa")
    if row.get('拉伸性能_抗拉强度_工程应力（MPa）'):
        performance.append(f"抗拉强度{row['拉伸性能_抗拉强度_工程应力（MPa）']}MPa")
    if row.get('拉伸性能_断后延伸率_工程应变（%）'):
        performance.append(f"断后延伸率{row['拉伸性能_断后延伸率_工程应变（%）']}%")
    
    # 硬度性能
    if row.get('硬度性能_硬度（HV）'):
        performance.append(f"硬度{row['硬度性能_硬度（HV）']}HV")
    
    # 疲劳性能
    if row.get('疲劳性能_疲劳强度（MPa）'):
        performance.append(f"疲劳强度{row['疲劳性能_疲劳强度（MPa）']}MPa")
    
    # 压缩性能
    if row.get('压缩性能_屈服强度_工程应力（MPa）'):
        performance.append(f"压缩屈服强度{row['压缩性能_屈服强度_工程应力（MPa）']}MPa")
    
    if performance:
        text_parts.append("主要力学性能包括：" + "、".join(performance))
    
    # 测试条件
    test_conditions = []
    if row.get('拉伸性能_测试温度（℃）'):
        test_conditions.append(f"测试温度{row['拉伸性能_测试温度（℃）']}℃")
    if row.get('疲劳性能_测试温度（℃）'):
        test_conditions.append(f"疲劳测试温度{row['疲劳性能_测试温度（℃）']}℃")
    
    if test_conditions:
        text_parts.append("测试条件：" + "，".join(test_conditions))
    
    # 应用信息
    application_info = []
    if row.get('应用领域'):
        application_info.append(f"应用领域：{row['应用领域']}")
    if row.get('服役环境'):
        application_info.append(f"服役环境：{row['服役环境']}")
    
    if application_info:
        text_parts.append("应用信息：" + "，".join(application_info))
    
    # 创新点（重要语义信息）
    if row.get('paper_innov'):
        # 简化创新点描述，避免过长
        innov_text = row['paper_innov']
        if len(innov_text) > 200:
            innov_text = innov_text[:200] + "..."
        text_parts.append(f"研究创新：{innov_text}")
    
    # 组合所有部分
    if text_parts:
        text = "。".join(text_parts) + "。"
    else:
        text = "数据记录信息不完整"
    
    return text


def extract_keywords(row):
    """
    提取关键词列表
    
    Args:
        row: pandas Series
        
    Returns:
        list: 关键词列表
    """
    keywords = set()
    
    # 合金相关
    if row.get('合金成分'):
        # 提取合金名称中的关键词
        alloy_text = row['合金成分']
        # 提取类似 Ti-6Al-4V 这样的合金名称
        alloy_matches = re.findall(r'[A-Za-z]+[-\dA-Za-z]+', alloy_text)
        keywords.update(alloy_matches)
        
        # 添加通用合金关键词
        if 'Ti' in alloy_text:
            keywords.add('钛合金')
        if 'Al' in alloy_text:
            keywords.add('铝合金')
    
    # 性能类型关键词
    performance_fields = ['拉伸', '疲劳', '硬度', '压缩', '冲击', '蠕变', '剪切', '腐蚀']
    for field in performance_fields:
        for col in row.keys():
            if field in str(col) and row[col] and str(row[col]).strip():
                keywords.add(f"{field}性能")
                break
    
    # 应用领域关键词
    if row.get('应用领域'):
        app_fields = row['应用领域'].split(';')
        for field in app_fields:
            if field.strip():
                keywords.add(field.strip())
    
    # 工艺类型关键词
    if row.get('制备工艺') and str(row['制备工艺']).strip():
        keywords.add('制备工艺')
    if row.get('热处理工艺') and str(row['热处理工艺']).strip():
        keywords.add('热处理')
    if row.get('加工工艺') and str(row['加工工艺']).strip():
        keywords.add('加工工艺')
    
    # 材料状态关键词
    if row.get('材料状态') and str(row['材料状态']).strip():
        keywords.add('材料状态')
    
    # 去除空字符串和None
    keywords = {kw for kw in keywords if kw and str(kw).strip()}
    
    return list(keywords)


def build_performance_summary(row):
    """
    构建性能数据摘要
    
    Args:
        row: pandas Series
        
    Returns:
        str: 性能数据摘要
    """
    summary_parts = []
    
    # 按性能类别分组
    performance_categories = {
        '力学性能': ['拉伸', '压缩', '剪切'],
        '疲劳性能': ['疲劳', '应力腐蚀疲劳'],
        '硬度性能': ['硬度'],
        '冲击性能': ['冲击'],
        '断裂性能': ['断裂韧性'],
        '蠕变性能': ['蠕变'],
        '热性能': ['热膨胀', '热导率'],
        '物理参数': ['密度', '弹性模量', '泊松比', '电导率', '电阻率']
    }
    
    for category, fields in performance_categories.items():
        has_data = False
        data_points = []
        
        for field in fields:
            # 查找包含该字段的列
            matching_cols = [
                col for col in row.keys() 
                if field in str(col) and row[col] and str(row[col]).strip()
            ]
            if matching_cols:
                has_data = True
                data_points.append(field)
        
        if has_data:
            summary_parts.append(f"{category}：{', '.join(data_points)}")
    
    if summary_parts:
        return "；".join(summary_parts)
    else:
        return "无详细性能数据"


def validate_text_generation(row):
    """
    验证文本生成结果
    
    Args:
        row: pandas Series
        
    Returns:
        dict: 验证结果
    """
    result = {
        'embedding_text_length': 0,
        'keywords_count': 0,
        'performance_summary_length': 0,
        'has_alloy_info': False,
        'has_performance_data': False,
        'has_application_info': False
    }
    
    # 生成文本
    embedding_text = build_embedding_text(row)
    keywords = extract_keywords(row)
    performance_summary = build_performance_summary(row)
    
    # 统计信息
    result['embedding_text_length'] = len(embedding_text)
    result['keywords_count'] = len(keywords)
    result['performance_summary_length'] = len(performance_summary)
    
    # 检查关键信息是否存在
    result['has_alloy_info'] = bool(row.get('合金成分'))
    result['has_performance_data'] = any(
        row.get(col) and str(row[col]).strip() 
        for col in row.keys() 
        if any(perf in str(col) for perf in ['拉伸', '疲劳', '硬度', '压缩', '冲击'])
    )
    result['has_application_info'] = bool(row.get('应用领域'))
    
    return result


if __name__ == "__main__":
    # 测试代码
    test_row = {
        'paper_title': 'FATIGUE PROPERTIES OF TI-6AL-4V',
        '合金成分': 'Ti–6Al–4V (wt.%)（TC4）',
        '材料状态': '接收态',
        '拉伸性能_屈服强度_工程应力（MPa）': '861',
        '拉伸性能_抗拉强度_工程应力（MPa）': '1009',
        '应用领域': '生物医学植入物',
        '服役环境': '人体体液环境',
        'paper_innov': '首次系统研究了TC4在生理盐水中的疲劳性能'
    }
    
    text = build_embedding_text(test_row)
    keywords = extract_keywords(test_row)
    summary = build_performance_summary(test_row)
    
    print("=== 文本生成测试 ===")
    print("嵌入文本:", text)
    print("关键词:", keywords)
    print("性能摘要:", summary)
    
    validation = validate_text_generation(test_row)
    print("验证结果:", validation)