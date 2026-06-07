#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API客户端
用于调用DeepSeek大模型生成失效诊断问问题
"""

import requests
import time
import json
from typing import Dict, Any, Optional


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "<deepseek-api-endpoint>"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # API调用统计
        self.call_count = 0
        self.error_count = 0
        
        print("DeepSeek客户端初始化完成")
    
    def generate_text(self, prompt: str, max_tokens: int = 300, 
                     temperature: float = 0.7, retry_count: int = 3) -> Optional[str]:
        """
        生成文本
        
        Args:
            prompt: 提示文本
            max_tokens: 最大token数
            temperature: 温度参数
            retry_count: 重试次数
            
        Returns:
            str: 生成的文本，失败返回None
        """
        
        # 构建请求数据
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        for attempt in range(retry_count):
            try:
                self.call_count += 1
                
                # 调用API
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 提取生成的文本
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0].get('message', {}).get('content', '')
                        
                        if content:
                            return content.strip()
                        else:
                            print(f"警告：第{attempt+1}次尝试返回空内容")
                    else:
                        print(f"警告：第{attempt+1}次尝试返回无效响应格式")
                
                elif response.status_code == 429:
                    # 频率限制，等待后重试
                    wait_time = (attempt + 1) * 10  # 指数退避
                    print(f"频率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    print(f"API调用失败 (状态码 {response.status_code}): {response.text}")
                    self.error_count += 1
            
            except requests.exceptions.Timeout:
                print(f"第{attempt+1}次尝试超时")
                self.error_count += 1
            
            except requests.exceptions.ConnectionError:
                print(f"第{attempt+1}次尝试连接错误")
                self.error_count += 1
            
            except Exception as e:
                print(f"第{attempt+1}次尝试发生未知错误: {str(e)}")
                self.error_count += 1
            
            # 重试前等待
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2  # 指数退避
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print(f"生成文本失败，已重试 {retry_count} 次")
        return None
    
    def batch_generate(self, prompts: list, max_tokens: int = 300, 
                      temperature: float = 0.7, batch_size: int = 3, 
                      delay: float = 2.0) -> list:
        """
        批量生成文本
        
        Args:
            prompts: 提示文本列表
            max_tokens: 最大token数
            temperature: 温度参数
            batch_size: 批次大小
            delay: 批次间延迟（秒）
            
        Returns:
            list: 生成的文本列表
        """
        
        results = []
        total_prompts = len(prompts)
        
        print(f"开始批量生成 {total_prompts} 个文本，批次大小: {batch_size}")
        
        for i in range(0, total_prompts, batch_size):
            batch_prompts = prompts[i:i + batch_size]
            batch_results = []
            
            # 处理当前批次
            for j, prompt in enumerate(batch_prompts):
                result = self.generate_text(prompt, max_tokens, temperature)
                batch_results.append(result)
                
                # 显示进度
                current_index = i + j + 1
                progress = current_index / total_prompts * 100
                print(f"进度: {current_index}/{total_prompts} ({progress:.1f}%)")
            
            results.extend(batch_results)
            
            # 批次间延迟（避免频率限制）
            if i + batch_size < total_prompts:
                print(f"等待 {delay} 秒后继续下一批次...")
                time.sleep(delay)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取API调用统计"""
        success_rate = (self.call_count - self.error_count) / self.call_count * 100 if self.call_count > 0 else 0
        
        return {
            "total_calls": self.call_count,
            "successful_calls": self.call_count - self.error_count,
            "failed_calls": self.error_count,
            "success_rate": f"{success_rate:.1f}%"
        }
    
    def validate_api_key(self) -> bool:
        """验证API密钥有效性"""
        try:
            # 简单的验证请求
            test_prompt = "请回复'测试成功'"
            result = self.generate_text(test_prompt, max_tokens=10)
            
            if result and "测试成功" in result:
                print("API密钥验证成功")
                return True
            else:
                print("API密钥验证失败")
                return False
        
        except Exception as e:
            print(f"API密钥验证出错: {str(e)}")
            return False


class MockDeepSeekClient:
    """模拟DeepSeek客户端（用于测试）"""
    
    def __init__(self, api_key: str = "mock_key"):
        self.api_key = api_key
        self.call_count = 0
        
        # 预定义的失效诊断问题模板
        self.question_templates = [
            "针对{alloy}在{application}中出现的{failure}问题，请分析根本原因、提出检测方法并制定修复预防措施。",
            "{alloy}制造的{application}发生{failure}失效，请进行系统性失效分析并提出解决方案。",
            "分析{alloy}在{application}应用中的{failure}失效机理，设计检测流程和预防策略。",
            "针对{alloy}的{application}部件出现的{failure}问题，请提出完整的诊断和修复方案。"
        ]
        
        print("模拟DeepSeek客户端初始化完成（测试模式）")
    
    def generate_text(self, prompt: str, max_tokens: int = 300, 
                     temperature: float = 0.7, retry_count: int = 3) -> Optional[str]:
        """模拟文本生成"""
        
        self.call_count += 1
        
        # 模拟API调用延迟
        time.sleep(0.2)
        
        # 从提示中提取信息
        scenario_info = self._extract_scenario_info(prompt)
        
        # 随机选择一个模板并填充
        template = self.question_templates[self.call_count % len(self.question_templates)]
        
        # 填充模板
        question = template.format(
            alloy=scenario_info.get('alloy', '钛合金'),
            application=scenario_info.get('application', '工程部件'),
            failure=scenario_info.get('failure', '失效')
        )
        
        return question
    
    def _extract_scenario_info(self, prompt: str) -> Dict[str, str]:
        """从提示中提取场景信息"""
        info = {}
        
        # 简单的关键词提取
        if 'TC4' in prompt or 'Ti-6Al-4V' in prompt:
            info['alloy'] = 'TC4钛合金'
        elif '航空航天' in prompt:
            info['application'] = '航空航天发动机叶片'
        elif '生物医学' in prompt:
            info['application'] = '生物医学植入物'
        elif '应力腐蚀' in prompt:
            info['failure'] = '应力腐蚀开裂'
        elif '疲劳' in prompt:
            info['failure'] = '疲劳断裂'
        elif '蠕变' in prompt:
            info['failure'] = '高温蠕变失效'
        
        return info
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_calls": self.call_count,
            "successful_calls": self.call_count,
            "failed_calls": 0,
            "success_rate": "100.0%",
            "mode": "模拟模式"
        }


# 测试函数
if __name__ == "__main__":
    # 测试模拟客户端
    client = MockDeepSeekClient()
    
    test_prompt = """
基于TC4钛合金在航空航天发动机叶片中出现的应力腐蚀开裂问题，生成失效诊断问题。
"""
    
    result = client.generate_text(test_prompt)
    print(f"生成的问题: {result}")
    
    stats = client.get_statistics()
    print(f"统计信息: {stats}")