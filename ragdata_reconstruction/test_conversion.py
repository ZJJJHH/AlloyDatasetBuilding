#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换功能测试脚本
用于验证数据转换的正确性和完整性
"""

import pandas as pd
import json
import os
import sys
from convert_ti_data import csv_row_to_json, validate_csv_structure
from text_generator import build_embedding_text, extract_keywords, build_performance_summary


def test_single_record():
    """测试单条记录转换"""
    print("=== 单条记录转换测试 ===")
    
    # 创建测试数据（包含所有必要的CSV列名）
    test_row = {
        'source_folder': 'test_folder',
        'lab_json_path': '/path/to/lab_json.txt',
        'paper_title': 'FATIGUE PROPERTIES OF TI-6AL-4V',
        'paper_authors': 'Author1; Author2',
        'paper_innov': '创新点描述',
        'entry_index_in_performance_data': 0,
        'parse_error': 'FALSE',
        'application': '[{"合金成分": "Ti-6Al-4V"}]',
        '合金成分': 'Ti–6Al–4V (wt.%)（TC4）',
        '材料状态': '接收态',
        '制备工艺': '铸造',
        '加工工艺': '',
        '锻造工艺': '',
        '轧制工艺': '',
        '热处理工艺': '退火',
        # 拉伸性能
        '拉伸性能_屈服强度_工程应力（MPa）': '861',
        '拉伸性能_抗拉强度_工程应力（MPa）': '1009',
        '拉伸性能_均匀延伸率_工程应变（%）': '',
        '拉伸性能_断后延伸率_工程应变（%）': '10',
        '拉伸性能_测试温度（℃）': '25',
        '拉伸性能_应变率（s^-1）': '',
        '拉伸性能_样品形状与尺寸': '',
        '拉伸性能_屈服强度_真实应力（MPa）': '',
        '拉伸性能_抗拉强度_真实应力（MPa）': '',
        '拉伸性能_均匀延伸率_真实应变（%）': '',
        '拉伸性能_断后延伸率_真实应变（%）': '',
        # 应力腐蚀疲劳性能
        '应力腐蚀疲劳性能_应力腐蚀疲劳强度（MPa）': '',
        '应力腐蚀疲劳性能_测试温度（℃）': '',
        '应力腐蚀疲劳性能_循环次数（次）': '',
        '应力腐蚀疲劳性能_腐蚀环境': '',
        # 疲劳性能
        '疲劳性能_疲劳强度（MPa）': '',
        '疲劳性能_测试温度（℃）': '',
        '疲劳性能_循环次数（次）': '',
        # 硬度性能
        '硬度性能_硬度（HV）': '350',
        '硬度性能_测试类型': '',
        '硬度性能': '',
        # 压缩性能
        '压缩性能_屈服强度_工程应力（MPa）': '',
        '压缩性能_抗压强度_工程应力（MPa）': '',
        '压缩性能_临界断裂应变_工程应变（%）': '',
        '压缩性能_测试温度（℃）': '',
        '压缩性能_应变率（s^-1）': '',
        '压缩性能_样品形状与尺寸': '',
        '压缩性能_屈服强度_真实应力（MPa）': '',
        '压缩性能_抗压强度_真实应力（MPa）': '',
        '压缩性能_临界断裂应变_真实应变（%）': '',
        # 夏比冲击性能
        '夏比冲击性能_冲击功（J）': '',
        '夏比冲击性能_冲击韧性（J/cm^2）': '',
        '夏比冲击性能_测试温度（℃）': '',
        '夏比冲击性能_缺口类型': '',
        # 其他性能
        '断裂韧性（MPa·m^(1/2)）': '',
        # 蠕变性能
        '蠕变性能_持久强度极限（MPa）': '',
        '蠕变性能_蠕变极限（MPa）': '',
        '蠕变性能_允许伸长率（%）': '',
        '蠕变性能_测试温度（℃）': '',
        '蠕变性能_测试时间（h）': '',
        # 剪切性能
        '剪切性能_剪切强度（MPa）': '',
        '剪切性能_测试温度（℃）': '',
        '剪切性能_应变率（s^-1）': '',
        # 物理性能
        '密度（g/cm^3）': '',
        '弹性模量（GPa）': '',
        '剪切模量（GPa）': '',
        '体积模量（GPa）': '',
        '比热容（J/(kg·℃)）': '',
        '熔点（℃）': '',
        '相变点温度（℃）': '',
        '泊松比': '',
        '热膨胀系数性能_热膨胀系数': '',
        '热膨胀系数性能_测试温度（℃）': '',
        '电阻率（Ω·cm）': '',
        '电导率（MS/m）': '',
        '热导率（W/(m·K)）': '',
        '测试温度（℃）': '',
        # 应用信息
        '应用领域': '生物医学植入物',
        '应用装备': '人工关节',
        '应用部件': '骨板',
        '服役环境': '人体体液环境',
        # 元素成分
        'Ag': '', 'Al': '6', 'Au': '', 'B': '', 'C': '', 'Co': '', 'Cr': '', 'Cu': '',
        'Fe': '', 'Ga': '', 'H': '', 'Hf': '', 'Mg': '', 'Mn': '', 'Mo': '', 'N': '',
        'Nb': '', 'Nd': '', 'Ni': '', 'O': '', 'P': '', 'Pd': '', 'Pt': '', 'S': '',
        'Si': '', 'Sn': '', 'Ta': '', 'Ti': '90', 'V': '4', 'W': '', 'Y': '', 'Zn': '', 'Zr': '', 'Be': ''
    }
    
    # 转换为Series
    row_series = pd.Series(test_row)
    
    # 执行转换
    json_data = csv_row_to_json(row_series)
    
    # 验证结果
    print("1. ID生成测试:", json_data['id'] == 'test_folder_0')
    print("2. 元数据完整性测试:", all(key in json_data['metadata'] for key in ['source_folder', 'paper_title', 'paper_authors']))
    print("3. 材料信息测试:", json_data['material_info']['合金成分'] == 'Ti–6Al–4V (wt.%)（TC4）')
    print("4. 性能数据测试:", json_data['performance_data']['拉伸性能_屈服强度_工程应力（MPa）'] == '861')
    print("5. 应用信息测试:", json_data['application_info']['应用领域'] == '生物医学植入物')
    print("6. 元素成分测试:", json_data['elemental_composition']['Al'] == '6')
    print("7. 嵌入文本测试:", len(json_data['embeddings']['text_for_embedding']) > 0)
    print("8. 关键词测试:", len(json_data['embeddings']['keywords']) > 0)
    print("9. 性能摘要测试:", len(json_data['embeddings']['performance_summary']) > 0)
    
    # 显示生成的文本
    print("\n生成的嵌入文本:")
    print(json_data['embeddings']['text_for_embedding'])
    
    return json_data


def test_text_generation():
    """测试文本生成功能"""
    print("\n=== 文本生成功能测试 ===")
    
    test_row = {
        'paper_title': 'TEST PAPER',
        '合金成分': 'Ti-5Al-2.5Sn',
        '材料状态': '热处理态',
        '制备工艺': '热等静压',
        '拉伸性能_屈服强度_工程应力（MPa）': '950',
        '硬度性能_硬度（HV）': '350',
        '应用领域': '航空航天',
        '服役环境': '高温高压环境'
    }
    
    row_series = pd.Series(test_row)
    
    # 测试各个文本生成函数
    embedding_text = build_embedding_text(row_series)
    keywords = extract_keywords(row_series)
    performance_summary = build_performance_summary(row_series)
    
    print("1. 嵌入文本长度:", len(embedding_text))
    print("2. 关键词数量:", len(keywords))
    print("3. 性能摘要长度:", len(performance_summary))
    print("4. 关键词内容:", keywords)
    print("5. 性能摘要:", performance_summary)
    
    return embedding_text, keywords, performance_summary


def test_csv_validation():
    """测试CSV结构验证"""
    print("\n=== CSV结构验证测试 ===")
    
    # 创建测试DataFrame
    test_data = {
        'source_folder': ['test1', 'test2'],
        'lab_json_path': ['/path1', '/path2'],
        'paper_title': ['Paper1', 'Paper2'],
        'paper_authors': ['Author1', 'Author2'],
        'paper_innov': ['Innov1', 'Innov2'],
        'entry_index_in_performance_data': [0, 1],
        'parse_error': ['FALSE', 'FALSE'],
        '合金成分': ['Ti-6Al-4V', 'Ti-5Al-2.5Sn'],
        '应用领域': ['生物医学', '航空航天']
    }
    
    df = pd.DataFrame(test_data)
    
    # 测试验证函数
    is_valid = validate_csv_structure(df)
    print("CSV结构验证结果:", is_valid)
    
    return is_valid


def test_sample_conversion():
    """测试小样本转换"""
    print("\n=== 小样本转换测试 ===")
    
    # 检查输入文件是否存在
    input_csv = '/path/to/data/csvdata/Ti_data.csv'
    if not os.path.exists(input_csv):
        print("输入文件不存在，跳过样本转换测试")
        return False
    
    try:
        # 读取前10条记录进行测试
        df = pd.read_csv(input_csv, nrows=10)
        df = df.fillna('')
        
        print(f"读取到 {len(df)} 条测试记录")
        
        # 转换每条记录
        for idx, row in df.iterrows():
            try:
                json_data = csv_row_to_json(row)
                
                # 基本验证
                assert 'id' in json_data
                assert 'metadata' in json_data
                assert 'embeddings' in json_data
                
                print(f"记录 {idx} 转换成功")
                
            except Exception as e:
                print(f"记录 {idx} 转换失败: {str(e)}")
                
        return True
        
    except Exception as e:
        print(f"样本转换测试失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=== 钛合金数据转换器测试套件 ===")
    
    # 执行各项测试
    test_results = {}
    
    test_results['single_record'] = test_single_record()
    test_results['text_generation'] = test_text_generation()
    test_results['csv_validation'] = test_csv_validation()
    test_results['sample_conversion'] = test_sample_conversion()
    
    print("\n=== 测试总结 ===")
    print("所有测试项目执行完成")
    
    # 检查是否有失败的项目
    failed_tests = [name for name, result in test_results.items() 
                   if result is False or (isinstance(result, tuple) and any(r is False for r in result))]
    
    if failed_tests:
        print(f"警告：以下测试项目失败: {failed_tests}")
        return 1
    else:
        print("所有测试通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())