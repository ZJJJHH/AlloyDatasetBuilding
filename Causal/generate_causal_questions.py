#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因果问（Does X cause Y）生成器
基于钛合金JSONL数据集，使用大模型生成因果关系分析问题
"""

import json
import os
import time
import random
from typing import List, Dict, Any
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient


class CausalQuestionGenerator:
    """因果问问题生成器"""
    
    def __init__(self, rag_retriever: RAGRetriever, deepseek_client: DeepSeekClient):
        self.rag_retriever = rag_retriever
        self.deepseek_client = deepseek_client
        self.generated_count = 0
        
        # 预定义的合金元素
        self.alloy_elements = [
            "Al", "V", "Sn", "Zr", "Mo", "Nb", "Ta", "Fe", 
            "Cr", "Ni", "Cu", "Si", "O", "N", "H", "C"
        ]
        
        # 预定义的工艺参数
        self.process_parameters = [
            "固溶处理温度", "时效处理温度", "冷却速率", 
            "变形量", "变形温度", "热处理时间",
            "退火温度", "淬火介质", "热加工工艺"
        ]
        
        # 预定义的性能指标
        self.performance_indicators = [
            "强度", "塑性", "韧性", "硬度", "疲劳性能", 
            "蠕变性能", "腐蚀性能", "断裂韧性", "热稳定性"
        ]
        
        # 预定义的影响关系类型
        self.causal_relationships = [
            "提高", "降低", "改善", "恶化", "增强", "减弱",
            "促进", "抑制", "优化", "劣化"
        ]
    
    def generate_causal_relationship(self, alloy_data: Dict) -> Dict[str, str]:
        """
        生成因果关系描述
        
        Args:
            alloy_data: 合金数据字典
            
        Returns:
            Dict: 因果关系描述
        """
        
        composition = alloy_data.get('material_info', {}).get('合金成分', '钛合金')
        application = alloy_data.get('application_info', {}).get('应用领域', '通用应用')
        
        # 提取合金中的主要元素
        main_elements = self._extract_main_elements(composition)
        
        # 随机选择因果关系类型
        causal_type = random.choice(["元素影响", "工艺影响", "复合影响"])
        
        if causal_type == "元素影响":
            # 元素对性能的影响
            cause = random.choice(main_elements) if main_elements else random.choice(self.alloy_elements)
            effect = random.choice(self.performance_indicators)
            relationship = random.choice(self.causal_relationships)
            
            scenario = {
                "causal_type": "元素影响",
                "cause": f"添加{cause}元素",
                "effect": effect,
                "relationship": relationship,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"分析{cause}元素对钛合金{effect}的影响机制"
            }
        
        elif causal_type == "工艺影响":
            # 工艺参数对性能的影响
            cause = random.choice(self.process_parameters)
            effect = random.choice(self.performance_indicators)
            relationship = random.choice(self.causal_relationships)
            
            scenario = {
                "causal_type": "工艺影响",
                "cause": f"调整{cause}",
                "effect": effect,
                "relationship": relationship,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"分析{cause}对钛合金{effect}的影响趋势"
            }
        
        else:  # 复合影响
            # 元素和工艺的复合影响
            element = random.choice(main_elements) if main_elements else random.choice(self.alloy_elements)
            process = random.choice(self.process_parameters)
            effect = random.choice(self.performance_indicators)
            relationship = random.choice(self.causal_relationships)
            
            scenario = {
                "causal_type": "复合影响",
                "cause": f"{element}元素含量和{process}",
                "effect": effect,
                "relationship": relationship,
                "alloy_composition": composition,
                "application_context": application,
                "description": f"分析{element}元素与{process}对钛合金{effect}的协同影响"
            }
        
        return scenario
    
    def _extract_main_elements(self, composition: str) -> List[str]:
        """从合金成分中提取主要元素"""
        elements = []
        
        # 简单的元素提取逻辑
        for element in self.alloy_elements:
            if element in composition:
                elements.append(element)
        
        return elements if elements else ["Al", "V"]  # 默认返回常见元素
    
    def generate_question_template(self, causal_scenario: Dict) -> str:
        """
        基于因果关系生成问题模板提示
        
        Args:
            causal_scenario: 因果关系描述
            
        Returns:
            str: 问题生成提示
        """
        
        prompt = f"""
你是一个材料科学专家，需要基于给定的钛合金数据生成因果关系分析问题。

因果关系：
- 合金成分：{causal_scenario['alloy_composition']}
- 应用背景：{causal_scenario['application_context']}
- 因果关系类型：{causal_scenario['causal_type']}
- 原因：{causal_scenario['cause']}
- 影响：{causal_scenario['effect']}
- 关系：{causal_scenario['relationship']}

请生成一个因果关系分析问题，要求：

1. 明确表述因果关系
   - 使用"是否...导致..."或"...对...有何影响"等句式
   - 体现具体的合金元素或工艺参数

2. 包含机制分析要求
   - 要求解释影响机理
   - 涉及微观组织变化
   - 考虑应用背景的影响

3. 体现科学性和专业性
   - 基于材料科学原理
   - 考虑实际工程应用
   - 体现系统性思考

问题要简洁明了，直接针对因果关系进行提问，不要包含解释性内容。
请直接生成问题，不要包含任何前缀或说明。
"""
        return prompt.strip()
    
    def generate_single_question(self) -> Dict[str, Any]:
        """生成单个因果问问题"""
        
        try:
            # 1. 从RAG系统中随机检索合金数据
            random_query = self._generate_random_query()
            retrieved_data = self.rag_retriever.retrieve(random_query, k=3)
            
            if not retrieved_data:
                return None
            
            # 随机选择一个合金数据
            selected_alloy = random.choice(retrieved_data)
            
            # 2. 生成因果关系
            causal_scenario = self.generate_causal_relationship(selected_alloy)
            
            # 3. 生成问题模板
            prompt = self.generate_question_template(causal_scenario)
            
            # 4. 调用DeepSeek API生成问题
            question = self.deepseek_client.generate_text(prompt, max_tokens=200)
            
            # 5. 清理问题文本
            question = self._clean_question_text(question)
            
            # 6. 构建完整的问题记录
            question_record = {
                "question_id": f"causal_{self.generated_count:06d}",
                "question_type": "causal",
                "question_text": question,
                "causal_scenario": causal_scenario,
                "reference_alloy": {
                    "composition": selected_alloy.get('material_info', {}).get('合金成分', ''),
                    "application": selected_alloy.get('application_info', {}).get('应用领域', ''),
                    "source_id": selected_alloy.get('id', '')
                },
                "metadata": {
                    "retrieved_query": random_query,
                    "retrieved_count": len(retrieved_data),
                    "model_used": "deepseek",
                    "causal_complexity": self._assess_causal_complexity(question)
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
            "钛合金 元素影响", "TC4 工艺参数", "Al元素 强度", 
            "热处理 性能", "V元素 韧性", "固溶处理 腐蚀",
            "变形量 疲劳", "时效处理 蠕变"
        ]
        return random.choice(queries)
    
    def _assess_causal_complexity(self, question: str) -> str:
        """评估因果关系复杂度"""
        question_lower = question.lower()
        
        # 根据关键词判断复杂度
        complexity_indicators = {
            "高级": ["协同作用", "交互影响", "微观机制", "相变过程", "热力学"],
            "中级": ["影响机理", "组织演变", "性能变化", "参数优化"],
            "初级": ["是否影响", "有何影响", "提高降低", "改善恶化"]
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
        
        print(f"开始生成 {target_count} 个因果问问题...")
        
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
            
            # 避免频繁调用API，添加延迟
            time.sleep(1.5)
        
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
            "question_type": "causal",
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
    
    print("=== 因果问问题生成器 ===")
    
    # 配置文件路径
    config = {
        "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
        "output_path": "/path/to/AlloyDatasetBuilding/Causal/causal_questions.json",
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
    generator = CausalQuestionGenerator(rag_retriever, deepseek_client)
    
    # 生成问题
    questions = generator.generate_batch_questions(config["target_question_count"])
    
    # 保存结果
    save_questions_to_json(questions, config["output_path"])
    
    # 显示统计信息
    print("\n=== 生成统计 ===")
    print(f"总问题数: {len(questions)}")
    
    # 因果关系类型分布
    causal_types = {}
    for q in questions:
        c_type = q['causal_scenario']['causal_type']
        causal_types[c_type] = causal_types.get(c_type, 0) + 1
    
    print("\n因果关系类型分布:")
    for c_type, count in causal_types.items():
        percentage = count / len(questions) * 100
        print(f"  {c_type}: {count} 条 ({percentage:.1f}%)")
    
    # 影响关系分布
    relationships = {}
    for q in questions:
        rel = q['causal_scenario']['relationship']
        relationships[rel] = relationships.get(rel, 0) + 1
    
    print("\n影响关系分布:")
    for rel, count in relationships.items():
        percentage = count / len(questions) * 100
        print(f"  {rel}: {count} 条 ({percentage:.1f}%)")
    
    # 性能指标分布
    performance_indicators = {}
    for q in questions:
        indicator = q['causal_scenario']['effect']
        performance_indicators[indicator] = performance_indicators.get(indicator, 0) + 1
    
    print("\n性能指标分布:")
    for indicator, count in performance_indicators.items():
        percentage = count / len(questions) * 100
        print(f"  {indicator}: {count} 条 ({percentage:.1f}%)")
    
    # 复杂度分布
    complexity_levels = {}
    for q in questions:
        complexity = q['metadata']['causal_complexity']
        complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
    
    print("\n问题复杂度分布:")
    for level, count in complexity_levels.items():
        percentage = count / len(questions) * 100
        print(f"  {level}: {count} 条 ({percentage:.1f}%)")


if __name__ == "__main__":
    main()