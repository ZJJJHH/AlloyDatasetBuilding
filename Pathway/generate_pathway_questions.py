#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机制问（Why/Pathway）生成器
基于钛合金JSONL数据集，使用大模型生成微观组织演变路径解释问题
"""

import json
import os
import time
import random
from typing import List, Dict, Any
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient


class PathwayQuestionGenerator:
    """机制问问题生成器"""
    
    def __init__(self, rag_retriever: RAGRetriever, deepseek_client: DeepSeekClient):
        self.rag_retriever = rag_retriever
        self.deepseek_client = deepseek_client
        self.generated_count = 0
        
        # 预定义的微观组织特征
        self.microstructural_features = [
            "α相", "β相", "α+β双相组织", "晶粒尺寸", "晶界特征",
            "析出相", "孪晶", "位错密度", "相界面", "织构"
        ]
        
        # 预定义的宏观性能
        self.macro_properties = [
            "强度", "塑性", "韧性", "硬度", "疲劳性能", 
            "蠕变性能", "腐蚀性能", "断裂韧性", "热稳定性"
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
    
    def generate_pathway_scenario(self, alloy_data: Dict) -> Dict[str, str]:
        """
        生成机制解释场景
        
        Args:
            alloy_data: 合金数据字典
            
        Returns:
            Dict: 机制解释场景描述
        """
        
        composition = alloy_data.get('material_info', {}).get('合金成分', '钛合金')
        application = alloy_data.get('application_info', {}).get('应用领域', '通用应用')
        
        # 随机选择机制解释类型
        pathway_type = random.choice(["微观组织演变", "性能形成机制", "工艺-结构-性能关联"])
        
        if pathway_type == "微观组织演变":
            # 微观组织演变路径
            micro_feature = random.choice(self.microstructural_features)
            process = random.choice(self.process_pathways)
            
            scenario = {
                "pathway_type": "微观组织演变",
                "micro_feature": micro_feature,
                "process": process,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"分析{composition}在{process}中{micro_feature}的演变路径"
            }
        
        elif pathway_type == "性能形成机制":
            # 性能形成机制
            macro_property = random.choice(self.macro_properties)
            mechanism = random.choice(self.mechanisms)
            
            scenario = {
                "pathway_type": "性能形成机制",
                "macro_property": macro_property,
                "mechanism": mechanism,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"解释{composition}中{macro_property}的{mechanism}机制"
            }
        
        else:  # 工艺-结构-性能关联
            # 完整的关联路径
            process = random.choice(self.process_pathways)
            micro_feature = random.choice(self.microstructural_features)
            macro_property = random.choice(self.macro_properties)
            
            scenario = {
                "pathway_type": "工艺-结构-性能关联",
                "process": process,
                "micro_feature": micro_feature,
                "macro_property": macro_property,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"分析{composition}中{process}→{micro_feature}→{macro_property}的关联路径"
            }
        
        return scenario
    
    def generate_question_template(self, pathway_scenario: Dict) -> str:
        """
        基于机制解释场景生成问题模板提示
        
        Args:
            pathway_scenario: 机制解释场景描述
            
        Returns:
            str: 问题生成提示
        """
        
        if pathway_scenario["pathway_type"] == "微观组织演变":
            prompt = f"""
你是一个材料科学专家，需要解释钛合金微观组织的演变路径。

场景信息：
- 合金成分：{pathway_scenario['alloy_composition']}
- 应用背景：{pathway_scenario['application_context']}
- 微观特征：{pathway_scenario['micro_feature']}
- 工艺过程：{pathway_scenario['process']}

请生成一个微观组织演变路径解释问题，要求：

1. 明确要求解释演变路径
   - 使用"如何演变"、"演变机制"、"演变路径"等表述
   - 体现从初始状态到最终状态的完整过程

2. 包含微观机制分析
   - 涉及相变、晶粒长大、析出等微观过程
   - 解释关键控制因素和影响因素
   - 考虑热力学和动力学原理

3. 体现科学性和系统性
   - 基于材料科学基本原理
   - 体现多尺度关联思维
   - 考虑实际应用背景的影响

问题要简洁明了，直接针对微观组织演变进行提问。
请直接生成问题，不要包含任何前缀或说明。
"""
        
        elif pathway_scenario["pathway_type"] == "性能形成机制":
            prompt = f"""
你是一个材料科学专家，需要解释钛合金宏观性能的形成机制。

场景信息：
- 合金成分：{pathway_scenario['alloy_composition']}
- 应用背景：{pathway_scenario['application_context']}
- 宏观性能：{pathway_scenario['macro_property']}
- 强化机制：{pathway_scenario['mechanism']}

请生成一个性能形成机制解释问题，要求：

1. 明确要求解释形成机制
   - 使用"形成机制"、"作用机理"、"影响机制"等表述
   - 体现微观组织与宏观性能的关联

2. 包含多层次机制分析
   - 原子尺度：元素分布、电子结构
   - 微观尺度：相组成、界面特征
   - 宏观尺度：性能表现、应用效果

3. 体现机制的系统性
   - 分析主要机制和辅助机制
   - 考虑不同机制的协同作用
   - 解释机制的控制因素

问题要简洁明了，直接针对性能形成机制进行提问。
请直接生成问题，不要包含任何前缀或说明。
"""
        
        else:  # 工艺-结构-性能关联
            prompt = f"""
你是一个材料科学专家，需要解释钛合金工艺-结构-性能的关联路径。

场景信息：
- 合金成分：{pathway_scenario['alloy_composition']}
- 应用背景：{pathway_scenario['application_context']}
- 工艺过程：{pathway_scenario['process']}
- 微观特征：{pathway_scenario['micro_feature']}
- 宏观性能：{pathway_scenario['macro_property']}

请生成一个工艺-结构-性能关联路径解释问题，要求：

1. 明确要求解释完整关联路径
   - 使用"关联路径"、"影响链条"、"作用路径"等表述
   - 体现从工艺到结构再到性能的完整链条

2. 包含多尺度关联分析
   - 工艺参数对微观组织的影响
   - 微观组织对宏观性能的影响
   - 各环节的关键控制因素

3. 体现系统工程思维
   - 分析正向影响和反馈机制
   - 考虑非线性关系和阈值效应
   - 解释优化路径和限制因素

问题要简洁明了，直接针对关联路径进行提问。
请直接生成问题，不要包含任何前缀或说明。
"""
        
        return prompt.strip()
    
    def generate_single_question(self) -> Dict[str, Any]:
        """生成单个机制问问题"""
        
        try:
            # 1. 从RAG系统中随机检索合金数据
            random_query = self._generate_random_query()
            retrieved_data = self.rag_retriever.retrieve(random_query, k=3)
            
            if not retrieved_data:
                return None
            
            # 随机选择一个合金数据
            selected_alloy = random.choice(retrieved_data)
            
            # 2. 生成机制解释场景
            pathway_scenario = self.generate_pathway_scenario(selected_alloy)
            
            # 3. 生成问题模板
            prompt = self.generate_question_template(pathway_scenario)
            
            # 4. 调用DeepSeek API生成问题（机制解释需要更多思考）
            question = self.deepseek_client.generate_text(prompt, max_tokens=250)
            
            # 5. 清理问题文本
            question = self._clean_question_text(question)
            
            # 6. 构建完整的问题记录
            question_record = {
                "question_id": f"pathway_{self.generated_count:06d}",
                "question_type": "pathway",
                "question_text": question,
                "pathway_scenario": pathway_scenario,
                "reference_alloy": {
                    "composition": selected_alloy.get('material_info', {}).get('合金成分', ''),
                    "application": selected_alloy.get('application_info', {}).get('应用领域', ''),
                    "source_id": selected_alloy.get('id', '')
                },
                "metadata": {
                    "retrieved_query": random_query,
                    "retrieved_count": len(retrieved_data),
                    "model_used": "deepseek",
                    "pathway_complexity": self._assess_pathway_complexity(question)
                }
            }
            
            self.generated_count += 1
            return question_record
            
        except Exception as e:
            print(f"生成问题时出错: {str(e)}")
            return None
    
    def _generate_random_query(self) -> str:
        """生成随机查询词"""
        queries = [
            "钛合金 微观组织", "TC4 相变机制", "α相 演变路径", 
            "热处理 组织演变", "β相 稳定性", "晶粒长大 机制",
            "析出强化 机理", "织构 形成机制"
        ]
        return random.choice(queries)
    
    def _assess_pathway_complexity(self, question: str) -> str:
        """评估机制解释复杂度"""
        question_lower = question.lower()
        
        # 根据关键词判断复杂度
        complexity_indicators = {
            "高级": ["多尺度", "协同作用", "非线性", "阈值", "反馈机制"],
            "中级": ["演变路径", "形成机制", "关联分析", "控制因素"],
            "初级": ["如何变化", "什么原因", "影响因素", "机制"]
        }
        
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in question_lower:
                    return level
        
        return "中级"
    
    def _clean_question_text(self, text: str) -> str:
        """清理问题文本"""
        # 移除可能的标记和多余空格
        text = text.strip()
        
        # 确保以问号或句号结尾
        if not any(text.endswith(punct) for punct in ['？', '?', '。', '.']):
            text += '？'
        
        # 移除可能的引用标记
        text = text.replace('问题：', '').replace('Question:', '').strip()
        
        return text
    
    def generate_batch_questions(self, target_count: int = 1000, progress_bar=None) -> List[Dict[str, Any]]:
        """批量生成问题"""
        
        print(f"开始生成 {target_count} 个机制问问题...")
        
        questions = []
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        # 创建或使用传入的进度条
        use_external_progress = progress_bar is not None
        if not use_external_progress:
            # 创建内部进度条
            try:
                from tqdm import tqdm
                progress_bar = tqdm(total=target_count, desc="生成进度", unit="条", ncols=100)
                tqdm_available = True
            except ImportError:
                tqdm_available = False
                print("提示：未安装tqdm库，使用简单进度显示")
                progress_bar = None
        
        while len(questions) < target_count:
            question = self.generate_single_question()
            
            if question:
                questions.append(question)
                success_count += 1
                
                # 更新进度条
                if progress_bar is not None:
                    progress_bar.update(1)
            else:
                error_count += 1
            
            # 避免频繁调用API，添加延迟（机制解释问题更复杂）
            time.sleep(2.0)
        
        # 关闭进度条（如果是内部创建的）
        if not use_external_progress and progress_bar is not None:
            progress_bar.close()
        
        total_time = time.time() - start_time
        print(f"\n生成完成！")
        print(f"成功生成: {success_count}")
        print(f"生成失败: {error_count}")
        print(f"总耗时: {total_time/60:.1f} 分钟")
        print(f"平均速度: {success_count/total_time*60:.1f} 条/分钟")
        
        return questions


def save_questions_to_json(questions: List[Dict], output_path: str):
    """保存问题到JSON文件"""
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 构建完整的输出数据
    output_data = {
        "metadata": {
            "total_questions": len(questions),
            "question_type": "pathway",
            "dataset_version": "1.0"
        },
        "questions": questions
    }
    
    # 保存到文件
    with open(output_path, 'w', encoding='utf-8-sig') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_path)
    print(f"问题已保存到: {output_path}")
    print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")


def main():
    """主函数"""
    
    print("=== 机制问问题生成器 ===")
    
    # 配置文件路径
    config = {
        "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
        "output_path": "/path/to/AlloyDatasetBuilding/Pathway/pathway_questions.json",
        "deepseek_api_key": "YOUR_DEEPSEEK_API_KEY",  # 需要替换为实际API密钥
        "target_question_count": 1000
    }
    
    # 检查数据文件是否存在
    if not os.path.exists(config["rag_data_path"]):
        print(f"错误：RAG数据文件不存在: {config['rag_data_path']}")
        return
    
    # 初始化组件
    print("初始化RAG检索器...")
    rag_retriever = RAGRetriever(config["rag_data_path"])
    
    print("初始化DeepSeek客户端...")
    deepseek_client = DeepSeekClient(config["deepseek_api_key"])
    
    # 初始化生成器
    generator = PathwayQuestionGenerator(rag_retriever, deepseek_client)
    
    # 生成问题
    questions = generator.generate_batch_questions(config["target_question_count"])
    
    # 保存结果
    save_questions_to_json(questions, config["output_path"])
    
    # 显示统计信息
    print("\n=== 生成统计 ===")
    print(f"总问题数: {len(questions)}")
    
    # 机制解释类型分布
    pathway_types = {}
    for q in questions:
        p_type = q['pathway_scenario']['pathway_type']
        pathway_types[p_type] = pathway_types.get(p_type, 0) + 1
    
    print("\n机制解释类型分布:")
    for p_type, count in pathway_types.items():
        percentage = count / len(questions) * 100
        print(f"  {p_type}: {count} 条 ({percentage:.1f}%)")
    
    # 微观特征分布
    micro_features = {}
    for q in questions:
        if 'micro_feature' in q['pathway_scenario']:
            feature = q['pathway_scenario']['micro_feature']
            micro_features[feature] = micro_features.get(feature, 0) + 1
    
    print("\n微观特征分布:")
    for feature, count in micro_features.items():
        percentage = count / len(questions) * 100
        print(f"  {feature}: {count} 条 ({percentage:.1f}%)")
    
    # 宏观性能分布
    macro_properties = {}
    for q in questions:
        if 'macro_property' in q['pathway_scenario']:
            property = q['pathway_scenario']['macro_property']
            macro_properties[property] = macro_properties.get(property, 0) + 1
    
    print("\n宏观性能分布:")
    for property, count in macro_properties.items():
        percentage = count / len(questions) * 100
        print(f"  {property}: {count} 条 ({percentage:.1f}%)")
    
    # 复杂度分布
    complexity_levels = {}
    for q in questions:
        complexity = q['metadata']['pathway_complexity']
        complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
    
    print("\n问题复杂度分布:")
    for level, count in complexity_levels.items():
        percentage = count / len(questions) * 100
        print(f"  {level}: {count} 条 ({percentage:.1f}%)")


if __name__ == "__main__":
    main()