#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证答案生成系统是否正常工作
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from config import LLM_MODEL, DEEPSEEK_CONFIG, RAG_CONFIG
        print(f"✓ config.py 导入成功")
        print(f"  - 使用模型: {LLM_MODEL}")
        print(f"  - RAG启用: {RAG_CONFIG['enable_rag']}")
    except Exception as e:
        print(f"✗ config.py 导入失败: {str(e)}")
        return False
    
    try:
        from rag_retriever import RAGRetriever
        print(f"✓ rag_retriever.py 导入成功")
    except Exception as e:
        print(f"✗ rag_retriever.py 导入失败: {str(e)}")
        return False
    
    try:
        from llm_client import get_llm_client
        print(f"✓ llm_client.py 导入成功")
    except Exception as e:
        print(f"✗ llm_client.py 导入失败: {str(e)}")
        return False
    
    try:
        from answer_generator import get_answer_generator
        print(f"✓ answer_generator.py 导入成功")
    except Exception as e:
        print(f"✗ answer_generator.py 导入失败: {str(e)}")
        return False
    
    return True


def test_rag_retriever():
    """测试RAG检索器"""
    print("\n测试RAG检索器...")
    try:
        from rag_retriever import RAGRetriever
        
        retriever = RAGRetriever("/path/to/AlloyDatasetBuilding/Ti_data.jsonl")
        print(f"✓ RAG检索器初始化成功")
        print(f"  - 加载数据: {retriever.data.__len__()} 条")
        
        # 测试检索
        results = retriever.retrieve("TC4 高强度 航空航天", question_type="what_if", k=3)
        print(f"✓ RAG检索测试成功")
        print(f"  - 检索结果: {len(results)} 条")
        
        return True
    except Exception as e:
        print(f"✗ RAG检索器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_client():
    """测试LLM客户端（仅测试初始化）"""
    print("\n测试LLM客户端初始化...")
    try:
        from llm_client import get_llm_client
        
        client = get_llm_client()
        print(f"✓ LLM客户端初始化成功")
        print(f"  - 使用模型: {client.model_name}")
        
        return True
    except Exception as e:
        print(f"✗ LLM客户端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_answer_generator():
    """测试答案生成器"""
    print("\n测试答案生成器...")
    try:
        from answer_generator import get_answer_generator
        
        # 测试反事实问生成器（最简单）
        generator = get_answer_generator('what_if')
        print(f"✓ 答案生成器初始化成功")
        print(f"  - 问题类型: {generator.question_type}")
        print(f"  - 问题数量: {generator.total_questions}")
        
        return True
    except Exception as e:
        print(f"✗ 答案生成器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("答案生成系统快速测试")
    print("="*60)
    
    results = []
    
    # 测试1：模块导入
    results.append(("模块导入", test_imports()))
    
    # 测试2：RAG检索器
    results.append(("RAG检索器", test_rag_retriever()))
    
    # 测试3：LLM客户端
    results.append(("LLM客户端", test_llm_client()))
    
    # 测试4：答案生成器
    results.append(("答案生成器", test_answer_generator()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n总计: {total_passed}/{total_tests} 通过")
    
    if total_passed == total_tests:
        print("\n✓ 所有测试通过！系统准备就绪。")
        print("\n下一步：编辑 config.py 设置API密钥，然后运行答案生成。")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
