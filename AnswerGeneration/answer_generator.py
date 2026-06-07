#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一答案生成框架
实现"统一框架+差异化生成"策略
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from tqdm import tqdm

from config import DATA_PATHS, GENERATION_CONFIG, RAG_CONFIG, LLM_MODEL
from rag_retriever import RAGRetriever
from llm_client import get_llm_client


class AnswerGenerator:
    """统一答案生成器框架"""
    
    def __init__(self, question_type: str):
        """
        初始化答案生成器
        
        Args:
            question_type: 问题类型（what_if, causal, mitigation, pathway）
        """
        self.question_type = question_type
        self.rag_retriever = RAGRetriever(RAG_CONFIG["data_path"])
        self.llm_client = get_llm_client()
        
        # 加载问题数据
        self.questions_path = DATA_PATHS.get(question_type)
        if not self.questions_path or not os.path.exists(self.questions_path):
            raise FileNotFoundError(f"问题文件不存在: {self.questions_path}")
        
        with open(self.questions_path, 'r', encoding='utf-8-sig') as f:
            self.data = json.load(f)
        
        self.questions = self.data.get('questions', [])
        self.total_questions = len(self.questions)
        
        # 中间结果文件路径
        self.intermediate_file = self.questions_path + ".intermediate"
        
        print(f"\n{'='*60}")
        print(f"答案生成器初始化完成")
        print(f"问题类型: {question_type}")
        print(f"问题数量: {self.total_questions}")
        print(f"使用模型: {LLM_MODEL}")
        print(f"{'='*60}\n")
    
    def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成单个问题的答案（子类实现差异化生成逻辑）
        
        Args:
            question_record: 问题记录
            
        Returns:
            Dict: 答案字典
        """
        raise NotImplementedError
    
    def _build_rag_context(self, question_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        构建RAG检索上下文
        
        Args:
            question_record: 问题记录
            
        Returns:
            List[Dict]: 检索到的相关数据
        """
        if not RAG_CONFIG["enable_rag"]:
            return []
        
        question_text = question_record.get('question_text', '')
        alloy_composition = question_record.get('reference_alloy', {}).get('composition', '')
        
        # 根据问题类型选择检索策略
        retrieved_data = self.rag_retriever.retrieve(
            query=question_text,
            question_type=self.question_type,
            k=RAG_CONFIG["retrieval_top_k"]
        )
        
        return retrieved_data
    
    def _extract_alloy_info(self, question_record: Dict[str, Any]) -> Dict[str, str]:
        """提取合金信息（使用所有场景字段）"""
        alloy_info = {
            'composition': question_record.get('reference_alloy', {}).get('composition', ''),
            'application': question_record.get('reference_alloy', {}).get('application', ''),
            'source_id': question_record.get('reference_alloy', {}).get('source_id', '')
        }
        
        # 从causal_scenario中提取额外信息
        if 'causal_scenario' in question_record:
            scenario = question_record['causal_scenario']
            alloy_info['causal_type'] = scenario.get('causal_type', '')
            alloy_info['cause'] = scenario.get('cause', '')
            alloy_info['effect'] = scenario.get('effect', '')
            alloy_info['relationship'] = scenario.get('relationship', '')
            alloy_info['alloy_composition'] = scenario.get('alloy_composition', '')
            alloy_info['application_context'] = scenario.get('application_context', '')
            alloy_info['description'] = scenario.get('description', '')
        
        # 从what_if_scenario中提取额外信息
        if 'what_if_scenario' in question_record:
            scenario = question_record['what_if_scenario']
            alloy_info['scenario_type'] = scenario.get('scenario_type', '')
            alloy_info['design_context'] = scenario.get('design_context', '')
            alloy_info['baseline_material'] = scenario.get('baseline_material', '')
            alloy_info['optimization_type'] = scenario.get('optimization_type', '')
            alloy_info['design_objective'] = scenario.get('design_objective', '')
            alloy_info['constraints'] = scenario.get('constraints', [])
            alloy_info['application_domain'] = scenario.get('application_domain', '')
            alloy_info['complexity_level'] = scenario.get('complexity_level', '')
            alloy_info['description'] = scenario.get('description', '')
        
        # 从pathway_scenario中提取额外信息
        if 'pathway_scenario' in question_record:
            scenario = question_record['pathway_scenario']
            alloy_info['pathway_type'] = scenario.get('pathway_type', '')
            alloy_info['process'] = scenario.get('process', '')
            alloy_info['macro_property'] = scenario.get('macro_property', '')
            alloy_info['alloy_composition'] = scenario.get('alloy_composition', '')
            alloy_info['application_context'] = scenario.get('application_context', '')
            alloy_info['description'] = scenario.get('description', '')
            alloy_info['micro_feature'] = scenario.get('micro_feature', '')
            alloy_info['mechanism'] = scenario.get('mechanism', '')
        
        # 从failure_scenario中提取额外信息
        if 'failure_scenario' in question_record:
            scenario = question_record['failure_scenario']
            alloy_info['failure_type'] = scenario.get('failure_type', '')
            alloy_info['symptoms'] = scenario.get('symptoms', '')
            alloy_info['alloy'] = scenario.get('alloy', '')
            alloy_info['application'] = scenario.get('application', '')
            alloy_info['operating_conditions'] = scenario.get('operating_conditions', '')
        
        # 从property_lookup_scenario中提取额外信息 - 已废弃
        # if 'property_lookup_scenario' in question_record:
        #     scenario = question_record['property_lookup_scenario']
        #     alloy_info['query_type'] = scenario.get('query_type', '')
        #     alloy_info['property_category'] = scenario.get('property_category', '')
        #     alloy_info['specific_property'] = scenario.get('specific_property', '')
        #     alloy_info['measurement_conditions'] = scenario.get('measurement_conditions', '')
        #     alloy_info['precision_requirement'] = scenario.get('precision_requirement', '')
        #     alloy_info['alloy_composition'] = scenario.get('alloy_composition', '')
        #     alloy_info['application_background'] = scenario.get('application_background', '')
        #     alloy_info['data_source'] = scenario.get('data_source', '')
        #     alloy_info['description'] = scenario.get('description', '')
        
        return alloy_info
    
    def _format_rag_context(self, retrieved_data: List[Dict[str, Any]]) -> str:
        """格式化RAG检索结果为文本"""
        if not retrieved_data:
            return ""
        
        context_parts = []
        for i, record in enumerate(retrieved_data, 1):
            alloy_info = record.get('material_info', {})
            perf_data = record.get('performance_data', {})
            app_info = record.get('application_info', {})
            
            part = f"[数据源 {i}]\n"
            part += f"合金成分: {alloy_info.get('合金成分', 'N/A')}\n"
            
            if perf_data:
                perf_str = ", ".join([f"{k}: {v}" for k, v in perf_data.items() if v])
                if perf_str:
                    part += f"性能数据: {perf_str}\n"
            
            if app_info:
                part += f"应用领域: {app_info.get('应用领域', 'N/A')}\n"
            
            context_parts.append(part)
        
        return "\n".join(context_parts)
    
    def _save_answer_to_question(self, question_record: Dict[str, Any], 
                                  answer: Dict[str, Any]) -> Dict[str, Any]:
        """
        将答案保存到问题记录中
        
        Args:
            question_record: 原始问题记录
            answer: 生成的答案
            
        Returns:
            Dict: 更新后的问题记录
        """
        answer_key = f"answer_{LLM_MODEL}"
        question_record[answer_key] = answer
        
        return question_record
    
    def process_batch(self, start_index: int = None, end_index: int = None,
                     save_interval: int = None) -> List[Dict[str, Any]]:
        """
        批量处理问题
        
        Args:
            start_index: 起始索引
            end_index: 结束索引
            save_interval: 保存间隔
            
        Returns:
            List[Dict]: 处理后的问题列表
        """
        if start_index is None:
            start_index = GENERATION_CONFIG.get("start_index", 0)
        if end_index is None:
            end_index = GENERATION_CONFIG.get("end_index", len(self.questions))
        if save_interval is None:
            save_interval = GENERATION_CONFIG.get("save_interval", 10)
        
        questions = self.questions[start_index:end_index]
        total_to_process = len(questions)
        
        print(f"\n{'='*60}")
        print(f"开始处理 {total_to_process} 个问题 (索引 {start_index} - {end_index})")
        print(f"{'='*60}\n")
        
        processed_questions = []
        success_count = 0
        error_count = 0
        
        # 创建进度条
        with tqdm(total=total_to_process, desc=f"处理{self.question_type}问题", 
                  unit="个", dynamic_ncols=True, 
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for i, question_record in enumerate(questions):
                try:
                    answer = self.generate_answer(question_record)
                    
                    updated_record = self._save_answer_to_question(question_record, answer)
                    processed_questions.append(updated_record)
                    
                    success_count += 1
                    
                    # 定期保存
                    if (i + 1) % save_interval == 0:
                        self._save_partial_results(processed_questions, start_index + i + 1)
                    
                    time.sleep(0.5)  # 避免过快调用
                    
                    # 更新进度条
                    pbar.update(1)
                    
                except Exception as e:
                    print(f"\n处理问题 {i+1} 时出错: {str(e)}")
                    error_count += 1
                    # 保留原始记录
                    processed_questions.append(question_record)
                    # 更新进度条（即使出错也更新）
                    pbar.update(1)
        
        print(f"\n处理完成!")
        print(f"成功: {success_count}")
        print(f"失败: {error_count}")
        
        return processed_questions
    
    def _save_partial_results(self, processed_questions: List[Dict], current_index: int):
        """保存中间结果到单一中间文件（增量写入）"""
        # 加载中间文件或创建新文件
        if os.path.exists(self.intermediate_file):
            with open(self.intermediate_file, 'r', encoding='utf-8-sig') as f:
                intermediate_data = json.load(f)
        else:
            # 创建新中间文件，复制原数据结构
            with open(self.questions_path, 'r', encoding='utf-8-sig') as f:
                original_data = json.load(f)
            intermediate_data = original_data.copy()
            intermediate_data['questions'] = []
        
        # 更新已处理的问题
        intermediate_data['questions'] = processed_questions
        
        # 保存到中间文件
        with open(self.intermediate_file, 'w', encoding='utf-8-sig') as f:
            json.dump(intermediate_data, f, ensure_ascii=False, indent=2)
        
        print(f"\r已保存中间结果到: {self.intermediate_file} (索引 {current_index})", end='', flush=True)
    
    def save_results(self, processed_questions: List[Dict[str, Any]], output_path: str = None):
        """
        保存最终结果
        
        Args:
            processed_questions: 处理后的问题列表
            output_path: 输出路径（可选）
        """
        if output_path is None:
            output_path = self.questions_path
        
        # 更新数据
        self.data['questions'] = processed_questions
        
        # 保存到原文件
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_path}")
        
        # 保存统计信息
        stats = self.llm_client.get_statistics()
        stats_path = output_path.replace('.json', f'_answer_stats_{LLM_MODEL}.json')
        with open(stats_path, 'w', encoding='utf-8-sig') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"统计信息已保存到: {stats_path}")
        
        # 删除中间文件
        if os.path.exists(self.intermediate_file):
            os.remove(self.intermediate_file)
            print(f"中间文件已清理: {self.intermediate_file}")
    
    def run(self, start_index: int = None, end_index: int = None):
        """
        运行答案生成流程
        
        Args:
            start_index: 起始索引
            end_index: 结束索引
        """
        print(f"\n{'='*60}")
        print(f"开始生成 {self.question_type} 类型问题的答案")
        print(f"{'='*60}\n")
        
        # 批量处理
        processed_questions = self.process_batch(start_index, end_index)
        
        # 保存结果
        self.save_results(processed_questions)
        
        print(f"\n{'='*60}")
        print(f"答案生成完成!")
        print(f"{'='*60}\n")


# PropertyLookupAnswerGenerator class - 已废弃，不再使用
# class PropertyLookupAnswerGenerator(AnswerGenerator):
#     """关联问答案生成器 - 侧重查表和精确匹配"""
#     
#     def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
#         """生成关联问答案"""
#         question_text = question_record.get('question_text', '')
#         alloy_info = self._extract_alloy_info(question_record)
#         
#         # RAG检索
#         retrieved_data = self._build_rag_context(question_record)
#         
#         # 构建提示
#         rag_context = self._format_rag_context(retrieved_data)
#         
#         prompt = f"""你是一个材料科学专家，需要基于钛合金数据回答属性查询问题。
# 
# 问题：
# {question_text}
# 
# 查询场景：
# - 查询类型：{alloy_info.get('query_type', '未知')}
# - 性能类别：{alloy_info.get('property_category', '未知')}
# - 具体性能：{alloy_info.get('specific_property', '未知')}
# - 测试条件：{alloy_info.get('measurement_conditions', '未知')}
# - 精度要求：{alloy_info.get('precision_requirement', '未知')}
# - 应用背景：{alloy_info.get('application_background', '未知')}
# - 数据来源：{alloy_info.get('data_source', '未知')}
# 
# 合金信息：
# - 合金成分：{alloy_info['composition']}
# - 应用领域：{alloy_info['application']}
# 
# """
#         
#         if rag_context:
#             prompt += f"""检索到的相关数据：
# {rag_context}
# 
# 请基于以上信息回答问题。如果数据中直接有答案，请给出具体数值；如果需要推断，请直接给出结果。"""
# 
#         prompt += """
# 
# 请严格按以下格式回答，不要包含任何推理过程、解释或Markdown格式：
# 答案：[具体数值或简要说明]
# 数据来源：[相关数据记录ID]
# 说明：[必要的补充说明，如测试条件等]"""
#         
#         # 调用LLM
#         answer_content = self.llm_client.generate_text(prompt, max_tokens=500)
#         
#         # 提取数据源
#         data_sources = []
#         if retrieved_data:
#             data_sources = [record.get('id', '') for record in retrieved_data]
#         
#         return {
#             "content": answer_content or "答案生成失败",
#             "data_sources": data_sources,
#             "model_used": self.llm_client.model_name
#         }


class WhatIfAnswerGenerator(AnswerGenerator):
    """反事实问答案生成器 - 侧重逻辑推理和方案设计"""
    
    def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
        """生成反事实问答案"""
        question_text = question_record.get('question_text', '')
        alloy_info = self._extract_alloy_info(question_record)
        
        # RAG检索
        retrieved_data = self._build_rag_context(question_record)
        
        # 构建提示
        rag_context = self._format_rag_context(retrieved_data)
        
        prompt = f"""你是一个材料设计专家，需要基于钛合金数据回答反事实设计问题。

问题：
{question_text}

设计场景：
- 场景类型：{alloy_info.get('scenario_type', '通用设计')}
- 设计背景：{alloy_info.get('design_context', '通用')}
- 基线材料：{alloy_info.get('baseline_material', '未知')}
- 优化类型：{alloy_info.get('optimization_type', '未知')}
- 设计目标：{alloy_info.get('design_objective', '未知')}
- 约束条件：{', '.join(alloy_info.get('constraints', [])) if alloy_info.get('constraints') else '无'}
- 应用领域：{alloy_info.get('application_domain', '通用')}
- 复杂度：{alloy_info.get('complexity_level', '未知')}

目标合金：
- 合金成分：{alloy_info['composition']}
- 应用领域：{alloy_info['application']}

"""
        
        if rag_context:
            prompt += f"""相关参考数据：
{rag_context}

请基于以上信息，结合材料科学原理，提出具体的反事实设计方案。"""

        prompt += """

请直接给出方案内容，不要包含任何推理过程、解释或Markdown格式。格式如下：
方案A：[方案名称]
- 设计策略：[具体成分/工艺调整]
- 预期效果：[性能提升预期]
- 微观机理：[组织演变解释]

方案B：[备选方案]
- 设计策略：[备选调整方案]
- 预期效果：[备选性能预期]
- 优势对比：[与方案A的对比]

方案选择建议：[综合评估和推荐]"""
        
        answer_content = self.llm_client.generate_text(prompt, max_tokens=1000)
        
        data_sources = [record.get('id', '') for record in retrieved_data] if retrieved_data else []
        
        return {
            "content": answer_content or "答案生成失败",
            "data_sources": data_sources,
            "model_used": self.llm_client.model_name
        }


class CausalAnswerGenerator(AnswerGenerator):
    """因果问答案生成器 - 侧重机理分析和因果推理"""
    
    def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
        """生成因果问答案"""
        question_text = question_record.get('question_text', '')
        alloy_info = self._extract_alloy_info(question_record)
        
        # RAG检索
        retrieved_data = self._build_rag_context(question_record)
        
        # 构建提示
        rag_context = self._format_rag_context(retrieved_data)
        
        prompt = f"""你是一个材料机理分析专家，需要回答钛合金的因果关系问题。

问题：
{question_text}

分析对象：
- 合金成分：{alloy_info['composition']}
- 应用背景：{alloy_info['application']}
- 因果类型：{alloy_info.get('causal_type', '未知')}
- 因素：{alloy_info.get('cause', '未知')}
- 影响：{alloy_info.get('effect', '未知')}
- 关系描述：{alloy_info.get('relationship', '未知')}
- 场景描述：{alloy_info.get('description', '未知')}

"""
        
        if rag_context:
            prompt += f"""相关参考数据：
{rag_context}

请基于材料科学原理，分析因果关系并解释机理。"""

        prompt += """

请直接给出分析内容，不要包含任何推理过程、解释或Markdown格式。格式如下：
1. 因果关系确认
   - 是否存在因果关系
   - 效应方向和强度

2. 作用机理分析
   - 微观机制：[原子/微观组织层面的解释]
   - 性能关联：[微观到宏观的桥梁]
   - 关键因素：[主要控制因素]

3. 影响因素评估
   - 内在因素：[成分/组织]
   - 外在因素：[工艺/条件]
   - 协同效应：[多因素交互]

4. 工程指导意义
   - 优化窗口：[可行的参数范围]
   - 设计准则：[具体建议]
   - 预警指标：[需要关注的阈值]"""
        
        answer_content = self.llm_client.generate_text(prompt, max_tokens=1200)
        
        data_sources = [record.get('id', '') for record in retrieved_data] if retrieved_data else []
        
        return {
            "content": answer_content or "答案生成失败",
            "data_sources": data_sources,
            "model_used": self.llm_client.model_name
        }


class MitigationAnswerGenerator(AnswerGenerator):
    """失效诊断问答案生成器 - 侧重系统性分析和解决方案"""
    
    def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
        """生成失效诊断问答案"""
        question_text = question_record.get('question_text', '')
        alloy_info = self._extract_alloy_info(question_record)
        
        # RAG检索
        retrieved_data = self._build_rag_context(question_record)
        
        # 构建提示
        rag_context = self._format_rag_context(retrieved_data)
        
        prompt = f"""你是一个材料失效分析专家，需要对钛合金失效事件进行系统性诊断。

失效场景：
{question_text}

失效场景详情：
- 失效类型：{alloy_info.get('failure_type', '未知')}
- 失效症状：{alloy_info.get('symptoms', '未知')}
- 合金成分：{alloy_info.get('alloy', alloy_info['composition'])}
- 应用领域：{alloy_info.get('application', '未知')}
- 工作条件：{alloy_info.get('operating_conditions', '未知')}

"""
        
        if rag_context:
            prompt += f"""相关参考案例：
{rag_context}

请基于以上信息，完成系统性失效分析。"""

        prompt += """

请直接给出分析内容，不要包含任何推理过程、解释或Markdown格式。格式如下：

1. 根本原因分析
   1.1 失效机理
       - 微观过程：[空洞形核→长大→连接→裂纹]
       - 关键驱动因素：[应力/温度/腐蚀等]
       - 微观组织敏感性：[相/晶界/第二相的影响]
   
   1.2 影响因素评估
       材料维度：[成分/组织/缺陷]
       工艺维度：[制造/热处理/加工]
       服役维度：[载荷/环境/温度]

2. 检测与验证方法
   2.1 无损检测：[超声/CT/涡流等]
   2.2 金相分析：[SEM/EBSD微观表征]
   2.3 断口分析：[特征识别]

3. 修复与预防措施
   3.1 紧急修复：[临时措施]
   3.2 长期改进：[材料/工艺/设计]
   3.3 监测预警：[服役监测方案]"""
        
        answer_content = self.llm_client.generate_text(prompt, max_tokens=1500)
        
        data_sources = [record.get('id', '') for record in retrieved_data] if retrieved_data else []
        
        return {
            "content": answer_content or "答案生成失败",
            "data_sources": data_sources,
            "model_used": self.llm_client.model_name
        }


class PathwayAnswerGenerator(AnswerGenerator):
    """机制问答案生成器 - 侧重路径完整性和多尺度关联"""
    
    def generate_answer(self, question_record: Dict[str, Any]) -> Dict[str, Any]:
        """生成机制问答案"""
        question_text = question_record.get('question_text', '')
        alloy_info = self._extract_alloy_info(question_record)
        
        # RAG检索
        retrieved_data = self._build_rag_context(question_record)
        
        # 构建提示
        rag_context = self._format_rag_context(retrieved_data)
        
        prompt = f"""你是一个材料机制解释专家，需要解释钛合金的微观组织演变路径和性能形成机制。

问题：
{question_text}

分析对象：
- 合金成分：{alloy_info['composition']}
- 应用背景：{alloy_info['application']}
- 路径类型：{alloy_info.get('pathway_type', '未知')}
- 场景描述：{alloy_info.get('description', '未知')}
- 应用场景：{alloy_info.get('application_context', '未知')}

"""
        
        if alloy_info.get('process'):
            prompt += f"- 工艺过程：{alloy_info['process']}\n"
        if alloy_info.get('macro_property'):
            prompt += f"- 宏观性能：{alloy_info['macro_property']}\n"
        if alloy_info.get('micro_feature'):
            prompt += f"- 微观特征：{alloy_info['micro_feature']}\n"
        if alloy_info.get('mechanism'):
            prompt += f"- 强化机制：{alloy_info['mechanism']}\n"
        
        if rag_context:
            prompt += f"""
相关参考数据：
{rag_context}

请基于材料科学原理，完整解释演变路径和机制。"""

        prompt += """

请直接给出路径解释内容，不要包含任何推理过程、解释或Markdown格式。格式如下：

完整演变路径：
阶段1：初始状态
- 微观组织特征
- 内能状态
- 缺陷分布

阶段2：演变过程
- 关键现象：[相变/析出/再结晶等]
- 驱动力：[热力学/动力学]
- 控制步骤：[速率决定因素]

阶段3：中间状态
- 亚稳态组织
- 残余应力
- 非平衡结构

阶段4：最终状态
- 稳定组织特征
- 性能表现
- 微观-宏观关联

影响因素分析：
- 工艺参数敏感性
- 材料成分影响
- 外部条件作用

路径调控策略：
- 关键控制点
- 抑制副反应
- 优化路径"""
        
        answer_content = self.llm_client.generate_text(prompt, max_tokens=1300)
        
        data_sources = [record.get('id', '') for record in retrieved_data] if retrieved_data else []
        
        return {
            "content": answer_content or "答案生成失败",
            "data_sources": data_sources,
            "model_used": self.llm_client.model_name
        }


def get_answer_generator(question_type: str) -> AnswerGenerator:
    """根据问题类型获取相应的答案生成器"""
    generators = {
        'what_if': WhatIfAnswerGenerator,
        'causal': CausalAnswerGenerator,
        'mitigation': MitigationAnswerGenerator,
        'pathway': PathwayAnswerGenerator
    }
    
    if question_type not in generators:
        raise ValueError(f"未知的问题类型: {question_type}")
    
    return generators[question_type](question_type)


if __name__ == "__main__":
    # 测试
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python answer_generator.py <question_type>")
        print("可用类型: what_if, causal, mitigation, pathway")
        sys.exit(1)
    
    question_type = sys.argv[1]
    
    try:
        generator = get_answer_generator(question_type)
        generator.run()
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
