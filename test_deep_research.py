#!/usr/bin/env python3
"""
Deep Research API 可用性测试脚本
用于验证您的 API key 是否有权限访问 Deep Research Agent
"""

import os
import time
from google import genai

def test_deep_research_access():
    """测试 Deep Research API 访问权限"""
    
    print("="*70)
    print("🧪 Deep Research API 可用性测试")
    print("="*70)
    
    # 1. 检查 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ 错误: 未找到 GEMINI_API_KEY 环境变量")
        print("\n💡 请先设置:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print(f"\n✅ API Key 已设置 (长度: {len(api_key)} 字符)")
    
    # 2. 初始化 Client
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini Client 初始化成功")
    except Exception as e:
        print(f"❌ Client 初始化失败: {e}")
        return False
    
    # 3. 测试简单的 Deep Research 调用
    print("\n" + "-"*70)
    print("📡 正在发送测试研究任务...")
    print("-"*70)
    
    test_prompt = """
    Research the latest news about Google Gemini AI in the past week.
    Provide a brief summary (200 words max) with at least 3 recent sources.
    """
    
    try:
        start_time = time.time()
        
        # 创建后台研究任务
        interaction = client.interactions.create(
            input=test_prompt,
            agent='deep-research-pro-preview-12-2025',
            background=True
        )
        
        print(f"✅ 任务已创建: {interaction.id}")
        print(f"📊 初始状态: {interaction.status}")
        print("\n⏳ 等待任务完成（预计 2-5 分钟）...\n")
        
        # 轮询检查状态
        poll_count = 0
        max_wait_time = 600  # 最多等待 10 分钟
        
        while True:
            poll_count += 1
            elapsed = time.time() - start_time
            
            # 获取最新状态
            interaction = client.interactions.get(interaction.id)
            status = interaction.status
            
            print(f"[{poll_count:2d}] ⏱️  {elapsed:5.1f}s | 状态: {status:15s}", end="")
            
            if status == "completed":
                print(" ✅")
                print("\n" + "="*70)
                print("🎉 测试成功！您的 API Key 可以访问 Deep Research!")
                print("="*70)
                
                # 显示结果
                if interaction.outputs and len(interaction.outputs) > 0:
                    result = interaction.outputs[-1].text
                    print(f"\n📝 研究结果预览 (前 500 字符):\n")
                    print("-"*70)
                    print(result[:500] + "..." if len(result) > 500 else result)
                    print("-"*70)
                    print(f"\n✅ 完整结果长度: {len(result)} 字符")
                    print(f"⏱️  总耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
                else:
                    print("\n⚠️ 任务完成但没有输出内容")
                
                return True
                
            elif status == "failed":
                print(" ❌")
                error_msg = getattr(interaction, 'error', '未知错误')
                print(f"\n❌ 研究任务失败: {error_msg}")
                return False
                
            else:
                print(f" (运行中...)")
                
                # 超时检查
                if elapsed > max_wait_time:
                    print(f"\n⏰ 超时：任务运行超过 {max_wait_time/60} 分钟")
                    print("💡 Deep Research 有时需要较长时间，您可以稍后检查任务状态")
                    return False
                
                # 等待 10 秒后再次检查
                time.sleep(10)
                
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("  1. 您的 API Key 尚未获得 Deep Research 访问权限")
        print("  2. 需要加入 Deep Research allowlist (白名单)")
        print("  3. API 配额已用完")
        print("\n💡 建议:")
        print("  - 检查 Google AI Studio 控制台")
        print("  - 申请 Deep Research 访问权限")
        print("  - 或继续使用现有的 generate_content 方案")
        return False


def test_fallback_method():
    """测试降级方案（使用标准 generate_content）"""
    
    print("\n" + "="*70)
    print("🔄 测试降级方案 (generate_content + Google Search)")
    print("="*70)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 需要 GEMINI_API_KEY")
        return False
    
    try:
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        
        print("\n📡 发送测试请求...")
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Search for the latest AI news from OpenAI and summarize in 100 words.",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        print("✅ 降级方案可用！")
        print(f"\n📝 响应预览 (前 300 字符):\n")
        print("-"*70)
        print(response.text[:300] + "..." if len(response.text) > 300 else response.text)
        print("-"*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 降级方案测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    
    # 测试 Deep Research
    deep_research_ok = test_deep_research_access()
    
    # 无论如何都测试降级方案
    print("\n")
    fallback_ok = test_fallback_method()
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试结果总结")
    print("="*70)
    print(f"  Deep Research API:    {'✅ 可用' if deep_research_ok else '❌ 不可用'}")
    print(f"  降级方案 (Fallback):  {'✅ 可用' if fallback_ok else '❌ 不可用'}")
    print("="*70)
    
    if deep_research_ok:
        print("\n🎉 建议: 可以开始迁移到 Deep Research!")
        print("   下一步: 运行 researcher_deep_research.py 进行完整测试")
    elif fallback_ok:
        print("\n⚠️  建议: Deep Research 暂不可用，但降级方案正常")
        print("   选项 1: 申请 Deep Research 访问权限")
        print("   选项 2: 继续使用当前的 researcher.py")
    else:
        print("\n❌ 两种方案都不可用，请检查:")
        print("   1. API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. API 配额是否充足")
    
    print("\n")
