#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反事实问题（What-if）生成器
基于钛合金JSONL数据集，使用DeepSeek API生成反事实设计问题
"""

import json
import os
import time
import random
from typing import List, Dict, Any
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient


class WhatIfQuestionGenerator:
    """反事实问题生成器"""
    
    def __init__(self, rag_retriever: RAGRetriever, deepseek_client: DeepSeekClient):
        self.rag_retriever = rag_retriever
        self.deepseek_client = deepseek_client
        self.generated_count = 0
        
        # 预定义的设计目标
        self.design_objectives = [
            "低成本高性能", "高温稳定性", "耐腐蚀性能", "轻量化设计",
            "高强度高韧性", "疲劳寿命优化", "工艺简化", "多功能集成"
        ]
        
        # 预定义的约束条件
        self.constraints = [
            "成本控制", "密度限制", "元素含量限制", "工艺复杂度",
            "环境友好性", "资源可获得性", "标准化要求", "安全性要求"
        ]
        
        # 预定义的应用领域
        self.application_domains = [
            "航空航天", "医疗器械", "汽车工业", "能源装备",
            "国防军工", "电子设备", "运动器材", "建筑结构"
        ]
        
        # 预定义的优化类型
        self.optimization_types = [
            "成分优化", "工艺调整", "结构设计", "性能平衡",
            "替代方案", "多目标优化", "逆向设计", "创新设计"
        ]
        
    def generate_question_template(self, what_if_scenario: Dict) -> str:
        """
        基于反事实设计场景生成问题模板提示
        
        Args:
            what_if_scenario: 反事实设计场景描述
            
        Returns:
            str: 问题生成提示
        """
        
        scenario_type = what_if_scenario["scenario_type"]
        design_context = what_if_scenario["design_context"]
        baseline_material = what_if_scenario["baseline_material"]
        optimization_type = what_if_scenario["optimization_type"]
        design_objective = what_if_scenario["design_objective"]
        constraints = what_if_scenario["constraints"]
        application_domain = what_if_scenario["application_domain"]
        
        if scenario_type == "材料设计优化":
            prompt = f"""
你是一个材料科学专家，需要生成一个材料设计优化问题。

场景信息：
- 设计背景：{design_context}
- 基线材料：{baseline_material}
- 优化类型：{optimization_type}
- 设计目标：{design_objective}
- 约束条件：{', '.join(constraints)}
- 应用领域：{application_domain}

请生成一个材料设计优化问题，要求：
1. 明确设计目标和约束条件
2. 体现逆向设计和优化思维
3. 问题要具体、有挑战性
4. 包含具体的性能指标和优化方向
5. 体现材料科学专业深度

请直接生成问题，不要包含任何前缀或说明。
"""
        
        elif scenario_type == "工艺路径优化":
            prompt = f"""
你是一个材料科学专家，需要生成一个工艺路径优化问题。

场景信息：
- 设计背景：{design_context}
- 基线材料：{baseline_material}
- 优化类型：{optimization_type}
- 设计目标：{design_objective}
- 约束条件：{', '.join(constraints)}
- 应用领域：{application_domain}

请生成一个工艺路径优化问题，要求：
1. 明确工艺调整的目标和约束
2. 体现工艺-结构-性能的关联思维
3. 问题要具体、可操作
4. 包含具体的工艺参数和优化方向
5. 体现制造工程的专业深度

请直接生成问题，不要包含任何前缀或说明。
"""
        
        elif scenario_type == "多目标优化设计":
            prompt = f"""
你是一个材料科学专家，需要生成一个多目标优化设计问题。

场景信息：
- 设计背景：{design_context}
- 基线材料：{baseline_material}
- 优化类型：{optimization_type}
- 设计目标：{design_objective}
- 约束条件：{', '.join(constraints)}
- 应用领域：{application_domain}

请生成一个多目标优化设计问题，要求：
1. 明确多个相互冲突的目标和约束
2. 体现权衡分析和优化策略
3. 问题要复杂、有挑战性
4. 包含具体的性能指标和优化方向
5. 体现系统工程思维

请直接生成问题，不要包含任何前缀或说明。
"""
        
        else:  # 逆向工程设计
            prompt = f"""
你是一个材料科学专家，需要生成一个逆向工程设计问题。

场景信息：
- 设计背景：{design_context}
- 基线材料：{baseline_material}
- 优化类型：{optimization_type}
- 设计目标：{design_objective}
- 约束条件：{', '.join(constraints)}
- 应用领域：{application_domain}

请生成一个逆向工程设计问题，要求：
1. 明确从目标到设计的逆向思维
2. 体现创新设计和替代方案
3. 问题要创新、有前瞻性
4. 包含具体的性能要求和设计方向
5. 体现材料设计的创新思维

请直接生成问题，不要包含任何前缀或说明。
"""
        
        return prompt.strip()
    
    def _extract_key_properties(self, alloy_data: Dict) -> str:
        """提取关键性能信息"""
        properties = []
        perf_data = alloy_data.get('performance_data', {})
        
        # 提取有数值的性能参数
        for prop_name, value in perf_data.items():
            if value and str(value).strip() and value != '':
                # 简化属性名称
                simplified_name = prop_name.split('_')[0] if '_' in prop_name else prop_name
                properties.append(f"{simplified_name}: {value}")
        
        # 限制最多显示5个关键性能
        if len(properties) > 5:
            properties = properties[:5]
        
        return ", ".join(properties) if properties else "性能数据不完整"
    
    def generate_what_if_scenario(self, alloy_data: Dict) -> Dict[str, str]:
        """
        生成反事实设计场景
        
        Args:
            alloy_data: 合金数据字典
            
        Returns:
            Dict: 反事实设计场景描述
        """
        
        composition = alloy_data.get('material_info', {}).get('合金成分', '钛合金')
        application = alloy_data.get('application_info', {}).get('应用领域', '通用应用')
        
        # 随机选择设计要素
        design_objective = random.choice(self.design_objectives)
        constraint = random.choice(self.constraints)
        application_domain = random.choice(self.application_domains)
        optimization_type = random.choice(self.optimization_types)
        
        # 根据优化类型构建场景
        if optimization_type == "成分优化":
            scenario = {
                "scenario_type": "材料设计优化",
                "design_context": f"{application_domain}应用",
                "baseline_material": composition,
                "optimization_type": "成分优化",
                "design_objective": design_objective,
                "constraints": [constraint],
                "application_domain": application_domain,
                "complexity_level": "高级",
                "description": f"在{constraint}约束下优化{composition}实现{design_objective}"
            }
        
        elif optimization_type == "工艺调整":
            scenario = {
                "scenario_type": "工艺路径优化",
                "design_context": f"{application_domain}制造",
                "baseline_material": composition,
                "optimization_type": "工艺调整",
                "design_objective": design_objective,
                "constraints": [constraint],
                "application_domain": application_domain,
                "complexity_level": "中级",
                "description": f"通过工艺调整优化{composition}的{design_objective}"
            }
        
        elif optimization_type == "多目标优化":
            # 多目标优化需要多个约束
            additional_constraint = random.choice([c for c in self.constraints if c != constraint])
            scenario = {
                "scenario_type": "多目标优化设计",
                "design_context": f"{application_domain}复杂应用",
                "baseline_material": composition,
                "optimization_type": "多目标优化",
                "design_objective": design_objective,
                "constraints": [constraint, additional_constraint],
                "application_domain": application_domain,
                "complexity_level": "高级",
                "description": f"平衡{constraint}和{additional_constraint}实现{design_objective}"
            }
        
        else:  # 逆向设计
            scenario = {
                "scenario_type": "逆向工程设计",
                "design_context": f"{application_domain}创新设计",
                "baseline_material": composition,
                "optimization_type": "逆向设计",
                "design_objective": design_objective,
                "constraints": [constraint],
                "application_domain": application_domain,
                "complexity_level": "高级",
                "description": f"从{design_objective}目标逆向设计{composition}的替代方案"
            }
        
        return scenario
    
    def generate_single_question(self) -> Dict[str, Any]:
        """生成单个反事实问题"""
        
        try:
            # 1. 从RAG系统中随机检索合金数据
            random_query = self._generate_random_query()
            retrieved_data = self.rag_retriever.retrieve(random_query, k=3)
            
            if not retrieved_data:
                return None
            
            # 随机选择一个合金数据
            selected_alloy = random.choice(retrieved_data)
            
            # 2. 生成反事实设计场景
            what_if_scenario = self.generate_what_if_scenario(selected_alloy)
            
            # 3. 基于场景生成问题模板
            prompt = self.generate_question_template(what_if_scenario)
            
            # 4. 调用DeepSeek API生成问题
            question = self.deepseek_client.generate_text(prompt, max_tokens=200)
            
            # 5. 清理问题文本
            question = self._clean_question_text(question)
            
            # 6. 构建完整的问题记录
            question_record = {
                "question_id": f"what_if_{self.generated_count:06d}",
                "question_type": "what_if",
                "question_text": question,
                "what_if_scenario": what_if_scenario,
                "reference_alloy": {
                    "composition": selected_alloy.get('material_info', {}).get('合金成分', ''),
                    "application": selected_alloy.get('application_info', {}).get('应用领域', ''),
                    "source_id": selected_alloy.get('id', '')
                },
                "metadata": {
                    "retrieved_query": random_query,
                    "retrieved_count": len(retrieved_data),
                    "model_used": "deepseek"
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
            "钛合金 高强度", "TC4 疲劳性能", "生物医学 植入物", 
            "航空航天 结构件", "耐腐蚀 钛合金", "高温 性能",
            "轻量化 设计", "成本优化", "工艺改进", "成分调整"
        ]
        return random.choice(queries)
    
    def _clean_question_text(self, text: str) -> str:
        """清理问题文本"""
        # 移除可能的标记和多余空格
        text = text.strip()
        
        # 确保以问号结尾
        if not text.endswith('？') and not text.endswith('?'):
            text += '？'
        
        # 移除可能的引用标记
        text = text.replace('问题：', '').replace('Question:', '').strip()
        
        return text
    
    def generate_batch_questions(self, target_count: int = 1000, progress_bar=None) -> List[Dict[str, Any]]:
        """批量生成问题"""
        
        print(f"开始生成 {target_count} 个反事实问题...")
        
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
            time.sleep(1)
        
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
            "question_type": "what_if",
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
    
    print("=== 反事实问题生成器 ===")
    
    # 配置文件路径
    config = {
        "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
        "output_path": "/path/to/AlloyDatasetBuilding/What_if/what_if_questions.json",
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
    generator = WhatIfQuestionGenerator(rag_retriever, deepseek_client)
    
    # 生成问题
    questions = generator.generate_batch_questions(config["target_question_count"])
    
    # 保存结果
    save_questions_to_json(questions, config["output_path"])
    
    # 显示统计信息
    print("\n=== 生成统计 ===")
    question_types = {}
    for q in questions:
        alloy_type = q['reference_alloy']['composition']
        if 'TC4' in alloy_type or 'Ti-6Al-4V' in alloy_type:
            question_types['TC4'] = question_types.get('TC4', 0) + 1
        elif 'Ti-5Al-2.5Sn' in alloy_type:
            question_types['Ti-5Al-2.5Sn'] = question_types.get('Ti-5Al-2.5Sn', 0) + 1
        else:
            question_types['其他'] = question_types.get('其他', 0) + 1
    
    print("问题类型分布:")
    for alloy_type, count in question_types.items():
        percentage = count / len(questions) * 100
        print(f"  {alloy_type}: {count} 条 ({percentage:.1f}%)")


if __name__ == "__main__":
    main()