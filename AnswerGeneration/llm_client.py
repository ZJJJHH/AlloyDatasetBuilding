#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型客户端 - 支持DeepSeek、Qwen、GLM和MiniMax
使用OpenAI库调用API，支持更多大模型
所有API密钥和参数可在config.py中配置
"""

from openai import OpenAI, RateLimitError, APIError
from typing import Dict, Any, Optional
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEEPSEEK_CONFIG, QWEN_CONFIG, GLM_CONFIG, MINIMAX_CONFIG, LLM_MODEL


class LLMClient:
    """大模型客户端基类"""
    
    def __init__(self, api_key: str, base_url: str, model: str, delay: float = 1.0):
        self.call_count = 0
        self.error_count = 0
        self.model_name = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.delay = delay
        print(f"LLM客户端初始化完成，使用模型: {self.model_name}")
    
    def generate_text(self, prompt: str, max_tokens: int = 1500, 
                     temperature: float = 0.7, retry_count: int = 3) -> Optional[str]:
        """生成文本（子类实现）"""
        raise NotImplementedError
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取API调用统计"""
        success_rate = (self.call_count - self.error_count) / self.call_count * 100 if self.call_count > 0 else 0
        
        return {
            "total_calls": self.call_count,
            "successful_calls": self.call_count - self.error_count,
            "failed_calls": self.error_count,
            "success_rate": f"{success_rate:.1f}%",
            "model": self.model_name
        }


class DeepSeekClient(LLMClient):
    """DeepSeek API客户端"""
    
    def __init__(self):
        config = DEEPSEEK_CONFIG
        super().__init__(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            delay=config.get("delay_between_calls", 1.0)
        )
        print(f"DeepSeek客户端初始化完成，模型: {self.model_name}")
    
    def generate_text(self, prompt: str, max_tokens: int = None, 
                     temperature: float = None, retry_count: int = None) -> Optional[str]:
        """生成文本"""
        if max_tokens is None:
            max_tokens = DEEPSEEK_CONFIG["max_tokens"]
        if temperature is None:
            temperature = DEEPSEEK_CONFIG["temperature"]
        if retry_count is None:
            retry_count = DEEPSEEK_CONFIG["retry_count"]
        
        for attempt in range(retry_count):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                
                if content:
                    if self.delay > 0:
                        import time
                        time.sleep(self.delay)
                    return content.strip()
                else:
                    print(f"警告：第{attempt+1}次尝试返回空内容")
                    self.error_count += 1
            
            except RateLimitError as e:
                wait_time = (attempt + 1) * 10
                print(f"频率限制，等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                continue
            
            except APIError as e:
                print(f"API调用失败: {str(e)}")
                self.error_count += 1
            
            except Exception as e:
                print(f"第{attempt+1}次尝试发生未知错误: {str(e)}")
                self.error_count += 1
            
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
        
        print(f"生成文本失败，已重试 {retry_count} 次")
        return None


class QwenClient(LLMClient):
    """Qwen API客户端（兼容DashScope API）"""
    
    def __init__(self):
        config = QWEN_CONFIG
        super().__init__(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            delay=config.get("delay_between_calls", 1.0)
        )
        print(f"Qwen客户端初始化完成，模型: {self.model_name}")
    
    def generate_text(self, prompt: str, max_tokens: int = None, 
                     temperature: float = None, retry_count: int = None) -> Optional[str]:
        """生成文本"""
        if max_tokens is None:
            max_tokens = QWEN_CONFIG["max_tokens"]
        if temperature is None:
            temperature = QWEN_CONFIG["temperature"]
        if retry_count is None:
            retry_count = QWEN_CONFIG["retry_count"]
        
        for attempt in range(retry_count):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                
                if content:
                    if self.delay > 0:
                        import time
                        time.sleep(self.delay)
                    return content.strip()
                else:
                    print(f"警告：第{attempt+1}次尝试返回空内容")
                    self.error_count += 1
            
            except RateLimitError as e:
                wait_time = (attempt + 1) * 10
                print(f"频率限制，等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                continue
            
            except APIError as e:
                print(f"API调用失败: {str(e)}")
                self.error_count += 1
            
            except Exception as e:
                print(f"第{attempt+1}次尝试发生未知错误: {str(e)}")
                self.error_count += 1
            
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
        
        print(f"生成文本失败，已重试 {retry_count} 次")
        return None


class GLMClient(LLMClient):
    """GLM API客户端（智谱AI）"""
    
    def __init__(self):
        config = GLM_CONFIG
        super().__init__(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            delay=config.get("delay_between_calls", 1.0)
        )
        print(f"GLM客户端初始化完成，模型: {self.model_name}")
    
    def generate_text(self, prompt: str, max_tokens: int = None, 
                     temperature: float = None, retry_count: int = None) -> Optional[str]:
        """生成文本"""
        if max_tokens is None:
            max_tokens = GLM_CONFIG["max_tokens"]
        if temperature is None:
            temperature = GLM_CONFIG["temperature"]
        if retry_count is None:
            retry_count = GLM_CONFIG["retry_count"]
        
        for attempt in range(retry_count):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                
                if content:
                    if self.delay > 0:
                        import time
                        time.sleep(self.delay)
                    return content.strip()
                else:
                    print(f"警告：第{attempt+1}次尝试返回空内容")
                    self.error_count += 1
            
            except RateLimitError as e:
                wait_time = (attempt + 1) * 10
                print(f"频率限制，等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                continue
            
            except APIError as e:
                print(f"API调用失败: {str(e)}")
                self.error_count += 1
            
            except Exception as e:
                print(f"第{attempt+1}次尝试发生未知错误: {str(e)}")
                self.error_count += 1
            
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
        
        print(f"生成文本失败，已重试 {retry_count} 次")
        return None


class MiniMaxClient(LLMClient):
    """MiniMax API客户端"""
    
    def __init__(self):
        config = MINIMAX_CONFIG
        super().__init__(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            delay=config.get("delay_between_calls", 1.0)
        )
        print(f"MiniMax客户端初始化完成，模型: {self.model_name}")
    
    def generate_text(self, prompt: str, max_tokens: int = None, 
                     temperature: float = None, retry_count: int = None) -> Optional[str]:
        """生成文本"""
        if max_tokens is None:
            max_tokens = MINIMAX_CONFIG["max_tokens"]
        if temperature is None:
            temperature = MINIMAX_CONFIG["temperature"]
        if retry_count is None:
            retry_count = MINIMAX_CONFIG["retry_count"]
        
        for attempt in range(retry_count):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                
                if content:
                    if self.delay > 0:
                        import time
                        time.sleep(self.delay)
                    return content.strip()
                else:
                    print(f"警告：第{attempt+1}次尝试返回空内容")
                    self.error_count += 1
            
            except RateLimitError as e:
                wait_time = (attempt + 1) * 10
                print(f"频率限制，等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
                continue
            
            except APIError as e:
                print(f"API调用失败: {str(e)}")
                self.error_count += 1
            
            except Exception as e:
                print(f"第{attempt+1}次尝试发生未知错误: {str(e)}")
                self.error_count += 1
            
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                import time
                time.sleep(wait_time)
        
        print(f"生成文本失败，已重试 {retry_count} 次")
        return None


def get_llm_client() -> LLMClient:
    """根据配置获取相应的LLM客户端"""
    if LLM_MODEL.lower() == 'deepseek':
        return DeepSeekClient()
    elif LLM_MODEL.lower() == 'qwen':
        return QwenClient()
    elif LLM_MODEL.lower() == 'glm':
        return GLMClient()
    elif LLM_MODEL.lower() == 'minimax':
        return MiniMaxClient()
    else:
        print(f"警告：未知的LLM模型 '{LLM_MODEL}'，默认使用DeepSeek")
        return DeepSeekClient()


if __name__ == "__main__":
    # 测试客户端
    client = get_llm_client()
    
    test_prompt = "请简要回答：TC4钛合金的典型抗拉强度是多少MPa？"
    
    result = client.generate_text(test_prompt, max_tokens=100)
    print(f"\n生成结果: {result}")
    
    stats = client.get_statistics()
    print(f"\n统计信息: {stats}")
