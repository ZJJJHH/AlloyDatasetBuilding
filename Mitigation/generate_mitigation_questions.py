#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失效诊断问（Root Cause + Tests + Mitigation）生成器
基于钛合金JSONL数据集，使用大模型生成工程失效诊断问题
"""

import json
import os
import time
import random
from typing import List, Dict, Any
from rag_retriever import RAGRetriever
from deepseek_client import DeepSeekClient


class MitigationQuestionGenerator:
    """失效诊断问问题生成器"""
    
    def __init__(self, rag_retriever: RAGRetriever, deepseek_client: DeepSeekClient):
        self.rag_retriever = rag_retriever
        self.deepseek_client = deepseek_client
        self.generated_count = 0
        
        # 预定义的失效场景模板
        self.failure_scenarios = [
            "应力腐蚀开裂", "疲劳断裂", "高温蠕变失效", "氢脆", 
            "腐蚀穿孔", "磨损失效", "冲击破坏", "热疲劳"
        ]
        
        # 预定义的应用场景
        self.application_scenarios = [
            "航空航天发动机叶片", "化工设备反应釜", "生物医学植入物",
            "海洋平台结构件", "汽车发动机部件", "核电站热交换器",
            "体育器材", "军工装备"
        ]
        
    def generate_failure_scenario(self, alloy_data: Dict) -> Dict[str, str]:
        """
        生成失效场景描述
        
        Args:
            alloy_data: 合金数据字典
            
        Returns:
            Dict: 失效场景描述
        """
        
        alloy_composition = alloy_data.get('material_info', {}).get('合金成分', '钛合金')
        application = alloy_data.get('application_info', {}).get('应用领域', '通用应用')
        
        # 根据合金特性和应用场景选择合适的失效模式
        failure_type = random.choice(self.failure_scenarios)
        application_context = random.choice(self.application_scenarios)
        
        # 构建失效场景描述
        scenario = {
            "alloy": alloy_composition,
            "application": application_context,
            "failure_type": failure_type,
            "symptoms": self._generate_symptoms(failure_type),
            "operating_conditions": self._generate_operating_conditions(application_context)
        }
        
        return scenario
    
    def _generate_symptoms(self, failure_type: str) -> str:
        """生成失效症状描述"""
        symptoms_map = {
            "应力腐蚀开裂": "出现裂纹，裂纹沿晶界扩展，表面有腐蚀产物",
            "疲劳断裂": "循环载荷作用下出现疲劳裂纹，断口呈现疲劳辉纹",
            "高温蠕变失效": "在高温下发生塑性变形，出现蠕变空洞和裂纹",
            "氢脆": "氢原子渗入导致脆性断裂，断口呈现沿晶或准解理特征",
            "腐蚀穿孔": "局部腐蚀导致材料减薄，最终形成穿孔",
            "磨损失效": "表面磨损导致尺寸变化，出现磨粒磨损或粘着磨损",
            "冲击破坏": "受到冲击载荷发生脆性断裂，断口呈现放射状花样",
            "热疲劳": "热循环作用下产生热应力裂纹，裂纹呈网状分布"
        }
        
        return symptoms_map.get(failure_type, "出现异常失效现象")
    
    def _generate_operating_conditions(self, application: str) -> str:
        """生成工作条件描述"""
        conditions_map = {
            "航空航天发动机叶片": "高温高压环境，承受离心力和气动载荷",
            "化工设备反应釜": "腐蚀性介质，高温高压，周期性操作",
            "生物医学植入物": "人体生理环境，承受循环载荷和腐蚀",
            "海洋平台结构件": "海水腐蚀环境，承受风浪载荷和疲劳",
            "汽车发动机部件": "高温振动环境，承受机械载荷和热应力",
            "核电站热交换器": "高温高压水环境，承受辐射和热应力",
            "体育器材": "冲击载荷环境，承受动态应力和磨损",
            "军工装备": "极端环境条件，承受冲击和腐蚀"
        }
        
        return conditions_map.get(application, "特定工作条件下")
    
    def generate_question_template(self, failure_scenario: Dict) -> str:
        """
        基于失效场景生成问题模板提示
        
        Args:
            failure_scenario: 失效场景描述
            
        Returns:
            str: 问题生成提示
        """
        
        prompt = f"""
你是一个材料失效分析专家，需要基于给定的钛合金失效场景生成完整的失效诊断问题。

失效场景：
- 材料：{failure_scenario['alloy']}
- 应用：{failure_scenario['application']}
- 失效类型：{failure_scenario['failure_type']}
- 失效症状：{failure_scenario['symptoms']}
- 工作条件：{failure_scenario['operating_conditions']}

请生成一个完整的失效诊断问题，要求包含以下三个核心部分：

1. 根本原因分析（Root Cause Analysis）
   - 分析可能的失效机理
   - 识别关键影响因素

2. 检测与诊断方法（Tests & Diagnosis）
   - 提出必要的检测手段
   - 设计诊断流程

3. 修复与预防措施（Mitigation & Prevention）
   - 制定修复方案
   - 提出预防措施

问题要体现工程实际，具有挑战性，要求模型进行系统性思考。
请直接生成完整的问题描述，不要包含任何解释或前缀。
"""
        return prompt.strip()
    
    def generate_single_question(self) -> Dict[str, Any]:
        """生成单个失效诊断问问题"""
        
        try:
            # 1. 从RAG系统中随机检索合金数据
            random_query = self._generate_random_query()
            retrieved_data = self.rag_retriever.retrieve(random_query, k=3)
            
            if not retrieved_data:
                return None
            
            # 随机选择一个合金数据
            selected_alloy = random.choice(retrieved_data)
            
            # 2. 生成失效场景
            failure_scenario = self.generate_failure_scenario(selected_alloy)
            
            # 3. 生成问题模板
            prompt = self.generate_question_template(failure_scenario)
            
            # 4. 调用DeepSeek API生成问题（需要更多tokens）
            question = self.deepseek_client.generate_text(prompt, max_tokens=300)
            
            # 5. 清理问题文本
            question = self._clean_question_text(question)
            
            # 6. 构建完整的问题记录
            question_record = {
                "question_id": f"mitigation_{self.generated_count:06d}",
                "question_type": "mitigation",
                "question_text": question,
                "failure_scenario": failure_scenario,
                "reference_alloy": {
                    "composition": selected_alloy.get('material_info', {}).get('合金成分', ''),
                    "application": selected_alloy.get('application_info', {}).get('应用领域', ''),
                    "source_id": selected_alloy.get('id', '')
                },
                "metadata": {
                    "retrieved_query": random_query,
                    "retrieved_count": len(retrieved_data),
                    "model_used": "deepseek",
                    "complexity_level": self._assess_complexity(question)
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
            "钛合金 失效分析", "TC4 疲劳断裂", "生物医学 腐蚀失效", 
            "航空航天 应力腐蚀", "高温 蠕变失效", "海洋环境 氢脆",
            "化工设备 磨损", "核电站 热疲劳"
        ]
        return random.choice(queries)
    
    def _assess_complexity(self, question: str) -> str:
        """评估问题复杂度"""
        question_lower = question.lower()
        
        # 根据关键词判断复杂度
        complexity_indicators = {
            "高级": ["多因素", "交互作用", "系统性", "微观机制", "定量分析"],
            "中级": ["影响因素", "检测方法", "预防措施", "机理分析"],
            "初级": ["原因", "措施", "检测", "修复"]
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
        
        print(f"开始生成 {target_count} 个失效诊断问问题...")
        
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
            
            # 避免频繁调用API，添加延迟（失效诊断问题更复杂，需要更多时间）
            time.sleep(2)
        
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
            "question_type": "mitigation",
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
    
    print("=== 失效诊断问问题生成器 ===")
    
    # 配置文件路径
    config = {
        "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
        "output_path": "/path/to/AlloyDatasetBuilding/Mitigation/mitigation_questions.json",
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
    generator = MitigationQuestionGenerator(rag_retriever, deepseek_client)
    
    # 生成问题
    questions = generator.generate_batch_questions(config["target_question_count"])
    
    # 保存结果
    save_questions_to_json(questions, config["output_path"])
    
    # 显示统计信息
    print("\n=== 生成统计 ===")
    print(f"总问题数: {len(questions)}")
    
    # 失效类型分布
    failure_types = {}
    for q in questions:
        f_type = q['failure_scenario']['failure_type']
        failure_types[f_type] = failure_types.get(f_type, 0) + 1
    
    print("\n失效类型分布:")
    for f_type, count in failure_types.items():
        percentage = count / len(questions) * 100
        print(f"  {f_type}: {count} 条 ({percentage:.1f}%)")
    
    # 应用场景分布
    application_scenes = {}
    for q in questions:
        app_scene = q['failure_scenario']['application']
        application_scenes[app_scene] = application_scenes.get(app_scene, 0) + 1
    
    print("\n应用场景分布:")
    for app_scene, count in application_scenes.items():
        percentage = count / len(questions) * 100
        print(f"  {app_scene}: {count} 条 ({percentage:.1f}%)")
    
    # 复杂度分布
    complexity_levels = {}
    for q in questions:
        complexity = q['metadata']['complexity_level']
        complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
    
    print("\n问题复杂度分布:")
    for level, count in complexity_levels.items():
        percentage = count / len(questions) * 100
        print(f"  {level}: {count} 条 ({percentage:.1f}%)")


if __name__ == "__main__":
    main()