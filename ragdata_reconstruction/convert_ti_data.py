#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钛合金数据CSV转JSONL格式转换器
用于将Ti_data.csv转换为适合大模型检索增强生成任务的JSONL格式
"""

import pandas as pd
import json
import os
import sys
import time
from datetime import datetime
from text_generator import build_embedding_text, extract_keywords, build_performance_summary

# 尝试导入tqdm进度条库，如果不可用则使用简单进度显示
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("提示：未安装tqdm库，将使用简单进度显示。安装命令：pip install tqdm")


def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except FileNotFoundError:
        print("配置文件不存在，使用默认配置")
        return {
            "input_csv": "/path/to/AlloyDatasetBuilding/Ti_data.csv",
            "output_jsonl": "Ti_data.jsonl",
            "encoding": "utf-8-sig",
            "chunk_size": 1000
        }


def validate_csv_structure(df):
    """验证CSV文件结构"""
    required_columns = [
        'source_folder', 'lab_json_path', 'paper_title', 'paper_authors', 
        'paper_innov', 'entry_index_in_performance_data', 'parse_error',
        '合金成分', '应用领域'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"警告：缺少必要列: {missing_columns}")
        return False
    
    print(f"CSV文件验证通过，共 {len(df.columns)} 列，{len(df)} 行")
    return True


def safe_get(row, column_name, default=''):
    """安全获取行数据，处理缺失的列"""
    try:
        return row[column_name]
    except KeyError:
        return default


def create_progress_bar(total, desc="处理进度"):
    """创建进度条"""
    if TQDM_AVAILABLE:
        return tqdm(total=total, desc=desc, unit="条", ncols=100)
    else:
        return SimpleProgressBar(total, desc)


class SimpleProgressBar:
    """简单的进度条实现（当tqdm不可用时使用）"""
    
    def __init__(self, total, desc="处理进度"):
        self.total = total
        self.desc = desc
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        
    def update(self, n=1):
        """更新进度"""
        self.current += n
        current_time = time.time()
        
        # 每处理100条记录或每5秒更新一次显示
        if self.current % 100 == 0 or current_time - self.last_update >= 5:
            self._display()
            self.last_update = current_time
    
    def _display(self):
        """显示进度"""
        elapsed = time.time() - self.start_time
        percent = (self.current / self.total) * 100
        
        if self.current > 0:
            speed = self.current / elapsed
            eta = (self.total - self.current) / speed if speed > 0 else 0
            eta_str = f"预计剩余: {eta:.1f}秒"
        else:
            speed = 0
            eta_str = "预计剩余: 计算中..."
        
        print(f"\r{self.desc}: {self.current}/{self.total} ({percent:.1f}%) | "
              f"速度: {speed:.1f}条/秒 | {eta_str}", end="", flush=True)
    
    def close(self):
        """完成进度条"""
        self._display()
        print()  # 换行


def format_file_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def is_empty_value(value):
    """判断值是否为空"""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ''
    if isinstance(value, (int, float)):
        return False  # 数值类型即使为0也不视为空
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def filter_empty_fields(data_dict, preserve_metadata=True):
    """
    递归过滤空值字段
    
    Args:
        data_dict: 要过滤的数据字典
        preserve_metadata: 是否保留metadata层的所有字段
    """
    if isinstance(data_dict, dict):
        filtered = {}
        
        for key, value in data_dict.items():
            # 如果是metadata层且需要保留，则不过滤空字段
            if preserve_metadata and key == 'metadata':
                filtered[key] = value
            else:
                filtered_value = filter_empty_fields(value, preserve_metadata)
                
                # 只有当过滤后的值不为空时才保留
                if not is_empty_value(filtered_value):
                    filtered[key] = filtered_value
        
        return filtered
    
    elif isinstance(data_dict, list):
        # 过滤列表中的空元素
        filtered_list = [filter_empty_fields(item, preserve_metadata) 
                        for item in data_dict 
                        if not is_empty_value(item)]
        return filtered_list
    
    else:
        # 基本数据类型直接返回
        return data_dict


def optimize_json_structure(json_data, row=None):
    """优化JSON结构，过滤空值字段"""
    
    # 应用空值过滤
    optimized_data = filter_empty_fields(json_data, preserve_metadata=True)
    
    # 特殊处理：确保embeddings字段始终存在
    if 'embeddings' not in optimized_data and row is not None:
        # 如果embeddings被过滤掉了，重新生成
        optimized_data['embeddings'] = {
            "text_for_embedding": build_embedding_text(row),
            "keywords": extract_keywords(row), 
            "performance_summary": build_performance_summary(row)
        }
    
    return optimized_data


def csv_row_to_json(row, optimize_structure=True):
    """将CSV行转换为目标JSON格式"""
    
    # 构建唯一ID
    record_id = f"{safe_get(row, 'source_folder')}_{safe_get(row, 'entry_index_in_performance_data')}"
    
    # 构建文本描述和关键词
    embedding_text = build_embedding_text(row)
    keywords = extract_keywords(row)
    performance_summary = build_performance_summary(row)
    
    # 完整的JSON结构
    json_data = {
        "id": record_id,
        "metadata": {
            "source_folder": safe_get(row, 'source_folder'),
            "lab_json_path": safe_get(row, 'lab_json_path'),
            "paper_title": safe_get(row, 'paper_title'),
            "paper_authors": safe_get(row, 'paper_authors'),
            "paper_innov": safe_get(row, 'paper_innov'),
            "entry_index_in_performance_data": safe_get(row, 'entry_index_in_performance_data'),
            "parse_error": safe_get(row, 'parse_error'),
            "application": safe_get(row, 'application')
        },
        "material_info": {
            "合金成分": safe_get(row, '合金成分'),
            "材料状态": safe_get(row, '材料状态'),
            "制备工艺": safe_get(row, '制备工艺'),
            "加工工艺": safe_get(row, '加工工艺'),
            "锻造工艺": safe_get(row, '锻造工艺'),
            "轧制工艺": safe_get(row, '轧制工艺'),
            "热处理工艺": safe_get(row, '热处理工艺')
        },
        "performance_data": {
            # 拉伸性能
            "拉伸性能_屈服强度_工程应力（MPa）": safe_get(row, '拉伸性能_屈服强度_工程应力（MPa）'),
            "拉伸性能_抗拉强度_工程应力（MPa）": safe_get(row, '拉伸性能_抗拉强度_工程应力（MPa）'),
            "拉伸性能_均匀延伸率_工程应变（%）": safe_get(row, '拉伸性能_均匀延伸率_工程应变（%）'),
            "拉伸性能_断后延伸率_工程应变（%）": safe_get(row, '拉伸性能_断后延伸率_工程应变（%）'),
            "拉伸性能_测试温度（℃）": safe_get(row, '拉伸性能_测试温度（℃）'),
            "拉伸性能_应变率（s^-1）": safe_get(row, '拉伸性能_应变率（s^-1）'),
            "拉伸性能_样品形状与尺寸": safe_get(row, '拉伸性能_样品形状与尺寸'),
            "拉伸性能_屈服强度_真实应力（MPa）": safe_get(row, '拉伸性能_屈服强度_真实应力（MPa）'),
            "拉伸性能_抗拉强度_真实应力（MPa）": safe_get(row, '拉伸性能_抗拉强度_真实应力（MPa）'),
            "拉伸性能_均匀延伸率_真实应变（%）": safe_get(row, '拉伸性能_均匀延伸率_真实应变（%）'),
            "拉伸性能_断后延伸率_真实应变（%）": safe_get(row, '拉伸性能_断后延伸率_真实应变（%）'),
            
            # 应力腐蚀疲劳性能
            "应力腐蚀疲劳性能_应力腐蚀疲劳强度（MPa）": safe_get(row, '应力腐蚀疲劳性能_应力腐蚀疲劳强度（MPa）'),
            "应力腐蚀疲劳性能_测试温度（℃）": safe_get(row, '应力腐蚀疲劳性能_测试温度（℃）'),
            "应力腐蚀疲劳性能_循环次数（次）": safe_get(row, '应力腐蚀疲劳性能_循环次数（次）'),
            "应力腐蚀疲劳性能_腐蚀环境": safe_get(row, '应力腐蚀疲劳性能_腐蚀环境'),
            
            # 疲劳性能
            "疲劳性能_疲劳强度（MPa）": safe_get(row, '疲劳性能_疲劳强度（MPa）'),
            "疲劳性能_测试温度（℃）": safe_get(row, '疲劳性能_测试温度（℃）'),
            "疲劳性能_循环次数（次）": safe_get(row, '疲劳性能_循环次数（次）'),
            
            # 硬度性能
            "硬度性能_硬度（HV）": safe_get(row, '硬度性能_硬度（HV）'),
            "硬度性能_测试类型": safe_get(row, '硬度性能_测试类型'),
            "硬度性能": safe_get(row, '硬度性能'),
            
            # 压缩性能
            "压缩性能_屈服强度_工程应力（MPa）": safe_get(row, '压缩性能_屈服强度_工程应力（MPa）'),
            "压缩性能_抗压强度_工程应力（MPa）": safe_get(row, '压缩性能_抗压强度_工程应力（MPa）'),
            "压缩性能_临界断裂应变_工程应变（%）": safe_get(row, '压缩性能_临界断裂应变_工程应变（%）'),
            "压缩性能_测试温度（℃）": safe_get(row, '压缩性能_测试温度（℃）'),
            "压缩性能_应变率（s^-1）": safe_get(row, '压缩性能_应变率（s^-1）'),
            "压缩性能_样品形状与尺寸": safe_get(row, '压缩性能_样品形状与尺寸'),
            "压缩性能_屈服强度_真实应力（MPa）": safe_get(row, '压缩性能_屈服强度_真实应力（MPa）'),
            "压缩性能_抗压强度_真实应力（MPa）": safe_get(row, '压缩性能_抗压强度_真实应力（MPa）'),
            "压缩性能_临界断裂应变_真实应变（%）": safe_get(row, '压缩性能_临界断裂应变_真实应变（%）'),
            
            # 夏比冲击性能
            "夏比冲击性能_冲击功（J）": safe_get(row, '夏比冲击性能_冲击功（J）'),
            "夏比冲击性能_冲击韧性（J/cm^2）": safe_get(row, '夏比冲击性能_冲击韧性（J/cm^2）'),
            "夏比冲击性能_测试温度（℃）": safe_get(row, '夏比冲击性能_测试温度（℃）'),
            "夏比冲击性能_缺口类型": safe_get(row, '夏比冲击性能_缺口类型'),
            
            # 其他性能
            "断裂韧性（MPa·m^(1/2)）": safe_get(row, '断裂韧性（MPa·m^(1/2)）'),
            
            # 蠕变性能
            "蠕变性能_持久强度极限（MPa）": safe_get(row, '蠕变性能_持久强度极限（MPa）'),
            "蠕变性能_蠕变极限（MPa）": safe_get(row, '蠕变性能_蠕变极限（MPa）'),
            "蠕变性能_允许伸长率（%）": safe_get(row, '蠕变性能_允许伸长率（%）'),
            "蠕变性能_测试温度（℃）": safe_get(row, '蠕变性能_测试温度（℃）'),
            "蠕变性能_测试时间（h）": safe_get(row, '蠕变性能_测试时间（h）'),
            
            # 剪切性能
            "剪切性能_剪切强度（MPa）": safe_get(row, '剪切性能_剪切强度（MPa）'),
            "剪切性能_测试温度（℃）": safe_get(row, '剪切性能_测试温度（℃）'),
            "剪切性能_应变率（s^-1）": safe_get(row, '剪切性能_应变率（s^-1）'),
            
            # 物理性能
            "密度（g/cm^3）": safe_get(row, '密度（g/cm^3）'),
            "弹性模量（GPa）": safe_get(row, '弹性模量（GPa）'),
            "剪切模量（GPa）": safe_get(row, '剪切模量（GPa）'),
            "体积模量（GPa）": safe_get(row, '体积模量（GPa）'),
            "比热容（J/(kg·℃)）": safe_get(row, '比热容（J/(kg·℃)）'),
            "熔点（℃）": safe_get(row, '熔点（℃）'),
            "相变点温度（℃）": safe_get(row, '相变点温度（℃）'),
            "泊松比": safe_get(row, '泊松比'),
            "热膨胀系数性能_热膨胀系数": safe_get(row, '热膨胀系数性能_热膨胀系数'),
            "热膨胀系数性能_测试温度（℃）": safe_get(row, '热膨胀系数性能_测试温度（℃）'),
            "电阻率（Ω·cm）": safe_get(row, '电阻率（Ω·cm）'),
            "电导率（MS/m）": safe_get(row, '电导率（MS/m）'),
            "热导率（W/(m·K)）": safe_get(row, '热导率（W/(m·K)）'),
            "测试温度（℃）": safe_get(row, '测试温度（℃）')
        },
        "application_info": {
            "应用领域": safe_get(row, '应用领域'),
            "应用装备": safe_get(row, '应用装备'),
            "应用部件": safe_get(row, '应用部件'),
            "服役环境": safe_get(row, '服役环境')
        },
        "elemental_composition": {
            "Ag": safe_get(row, 'Ag'), "Al": safe_get(row, 'Al'), "Au": safe_get(row, 'Au'), "B": safe_get(row, 'B'),
            "C": safe_get(row, 'C'), "Co": safe_get(row, 'Co'), "Cr": safe_get(row, 'Cr'), "Cu": safe_get(row, 'Cu'),
            "Fe": safe_get(row, 'Fe'), "Ga": safe_get(row, 'Ga'), "H": safe_get(row, 'H'), "Hf": safe_get(row, 'Hf'),
            "Mg": safe_get(row, 'Mg'), "Mn": safe_get(row, 'Mn'), "Mo": safe_get(row, 'Mo'), "N": safe_get(row, 'N'),
            "Nb": safe_get(row, 'Nb'), "Nd": safe_get(row, 'Nd'), "Ni": safe_get(row, 'Ni'), "O": safe_get(row, 'O'),
            "P": safe_get(row, 'P'), "Pd": safe_get(row, 'Pd'), "Pt": safe_get(row, 'Pt'), "S": safe_get(row, 'S'),
            "Si": safe_get(row, 'Si'), "Sn": safe_get(row, 'Sn'), "Ta": safe_get(row, 'Ta'), "Ti": safe_get(row, 'Ti'),
            "V": safe_get(row, 'V'), "W": safe_get(row, 'W'), "Y": safe_get(row, 'Y'), "Zn": safe_get(row, 'Zn'),
            "Zr": safe_get(row, 'Zr'), "Be": safe_get(row, 'Be')
        },
        "embeddings": {
            "text_for_embedding": embedding_text,
            "keywords": keywords,
            "performance_summary": performance_summary
        }
    }
    
    # 应用结构优化（过滤空值字段）
    if optimize_structure:
        json_data = filter_empty_fields(json_data, preserve_metadata=True)
    
    return json_data


def convert_csv_to_jsonl(csv_path, output_path, encoding='utf-8', chunk_size=1000):
    """将CSV转换为JSONL格式"""
    
    print(f"开始转换: {csv_path}")
    print(f"输出文件: {output_path}")
    
    try:
        # 读取CSV文件
        print("正在读取CSV文件...")
        df = pd.read_csv(csv_path, encoding=encoding)
        
        # 数据预处理
        df = df.fillna('')
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        # 验证数据结构
        if not validate_csv_structure(df):
            print("CSV文件结构验证失败，请检查文件格式")
            return False
        
        total_records = len(df)
        processed_count = 0
        error_count = 0
        
        # 创建进度条
        progress_bar = create_progress_bar(total_records, "数据转换进度")
        
        print(f"开始处理 {total_records} 条记录...")
        
        # 分批处理大文件
        with open(output_path, 'w', encoding='utf-8') as f:
            for start_idx in range(0, total_records, chunk_size):
                end_idx = min(start_idx + chunk_size, total_records)
                chunk_df = df.iloc[start_idx:end_idx]
                
                for idx, row in chunk_df.iterrows():
                    try:
                        json_data = csv_row_to_json(row)
                        f.write(json.dumps(json_data, ensure_ascii=False) + '\n')
                        processed_count += 1
                        
                        # 更新进度条
                        progress_bar.update(1)
                            
                    except Exception as e:
                        error_count += 1
                        print(f"\n处理第 {idx} 行时出错: {str(e)}")
                        continue
        
        # 关闭进度条
        progress_bar.close()
        
        # 计算处理时间
        if hasattr(progress_bar, 'start_time'):
            elapsed_time = time.time() - progress_bar.start_time
        else:
            elapsed_time = progress_bar.format_dict.get('elapsed', 0)
        
        # 输出统计信息
        print(f"\n转换完成！")
        print(f"总记录数: {total_records}")
        print(f"成功处理: {processed_count}")
        print(f"处理错误: {error_count}")
        print(f"处理时间: {elapsed_time:.2f} 秒")
        print(f"平均速度: {processed_count/elapsed_time:.1f} 条/秒" if elapsed_time > 0 else "平均速度: 计算中...")
        
        # 输出文件信息
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"输出文件大小: {format_file_size(file_size)}")
        
        return processed_count > 0
        
    except Exception as e:
        print(f"转换过程出错: {str(e)}")
        return False


def main():
    """主函数"""
    print("=== 钛合金数据CSV转JSONL转换器 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载配置
    config = load_config()
    
    # 检查输入文件是否存在
    if not os.path.exists(config['input_csv']):
        print(f"错误：输入文件不存在: {config['input_csv']}")
        sys.exit(1)
    
    # 执行转换
    success = convert_csv_to_jsonl(
        csv_path=config['input_csv'],
        output_path=config['output_jsonl'],
        encoding=config['encoding'],
        chunk_size=config['chunk_size']
    )
    
    if success:
        print(f"转换成功完成！")
        print(f"输出文件: {os.path.abspath(config['output_jsonl'])}")
    else:
        print("转换失败！")
        sys.exit(1)
    
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()