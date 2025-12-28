---
description: 将项目从 Gemini generate_content 迁移到 Deep Research API
---

# 🔄 迁移到 Deep Research API 实施计划

## 📊 现状分析

### 当前实现方式
您的项目目前使用 `gemini-3-pro-preview` 模型通过 `generate_content` API，配合：
- **Google Search Grounding**: 实时搜索网络信息
- **Thinking Mode**: 包含思考过程
- **结构化 Prompt**: 手动设计的详细提示词

### 核心问题
1. **深度不足**: 直接对话模式只进行一次搜索和生成，缺乏多轮深入研究
2. **覆盖面有限**: 可能遗漏重要信息源
3. **质量不稳定**: 依赖单次输出的质量

---

## 🎯 迁移目标

使用 **Deep Research API** 替换当前方案，获得：
1. ✅ **自动多轮研究**: AI 自主规划搜索策略并多次迭代
2. ✅ **更深入的分析**: 自动分析收集到的信息并生成详细报告
3. ✅ **结构化引用**: 自动提供来源 URL 和时间戳
4. ✅ **更高的信息密度**: 从更多来源聚合信息

---

## 🛠️ 技术实施方案

### Phase 1: API 访问测试 (预计 1 小时)

#### 1.1 获取 Deep Research 访问权限
- [ ] 访问 [Google AI Studio](https://aistudio.google.com)
- [ ] 检查 API key 是否已启用 Deep Research
- [ ] 测试 Interactions API 是否可用（可能需要加入 allowlist）

#### 1.2 添加依赖包
更新 `requirements.txt`:
```
google-genai>=1.0.0
notion-client
PyGithub
markdown
```

#### 1.3 创建测试脚本
创建 `test_deep_research.py` 验证 API 访问:
```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 测试 Deep Research
response = client.agents.interact(
    agent_id="deep-research-agent",
    prompt="Search for latest AI news from the past 24 hours"
)
print(response)
```

---

### Phase 2: 重构核心研究函数 (预计 2-3 小时)

#### 2.1 创建新的 `run_deep_research()` 函数
替换现有的 `run_gemini3_research()`:

```python
def run_deep_research():
    """使用 Gemini Deep Research Agent 进行每日深度研究"""
    print("🔬 正在启动 Deep Research Agent...")
    
    current_date = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    yesterday = (datetime.now(TZ_CN) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Deep Research 专用 Prompt（更简洁，让 Agent 自主规划）
    research_query = f"""
    Research Task: AI Industry Intelligence Report for {current_date}
    
    Timeframe: {yesterday} to today ({current_date})
    
    Research Objectives:
    1. Identify the 4-6 most significant AI-related events in the past 24 hours
    2. Cover multiple dimensions:
       - Major product launches or announcements (OpenAI, Google, Anthropic, Meta, NVIDIA)
       - Breakthrough papers on ArXiv or HuggingFace
       - Trending open-source projects on GitHub
       - Industry news (funding, talent movement, business analysis)
    3. Find community discussions on Reddit/HackerNews/Twitter
    
    Search Strategy:
    - Official sources: site:openai.com/blog, site:anthropic.com, site:deepmind.google
    - News: "AI news after:{yesterday}", VentureBeat AI, TechCrunch AI
    - Community: site:reddit.com/r/LocalLlama, site:news.ycombinator.com, site:huggingface.co/papers
    - GitHub: "AI trending repositories"
    
    Output Requirements:
    - Write a comprehensive report in Chinese (Simplified)
    - Include verified URLs with timestamps
    - Provide deep analysis, not just summaries
    - Structure the report with clear sections
    - Highlight WHY each piece of news matters
    
    Target Audience: AI professionals and enthusiasts who need high signal-to-noise ratio intelligence
    """
    
    try:
        # 调用 Deep Research Agent
        response = client.agents.interact(
            agent_id="deep-research-agent",
            prompt=research_query,
            config=types.InteractionConfig(
                response_modality="TEXT",  # 输出纯文本报告
                include_sources=True,      # 包含来源引用
            )
        )
        
        # Deep Research 返回格式可能不同，需要适配
        return response.text
        
    except Exception as e:
        print(f"❌ Deep Research 调用失败: {e}")
        print("🔄 降级到原有的 generate_content 方案...")
        return run_gemini3_research_fallback()
```

#### 2.2 保留降级方案
将原有的 `run_gemini3_research()` 重命名为 `run_gemini3_research_fallback()`:
- 当 Deep Research 不可用时自动降级
- 保证服务稳定性

#### 2.3 更新响应解析逻辑
Deep Research 的输出格式可能与当前不同，需要：
1. 分析实际返回结构
2. 更新 `parse_gemini_response()` 函数
3. 可能需要使用 AI 二次处理，将 Deep Research 的报告转换为您的标准格式

---

### Phase 3: 输出格式适配 (预计 1-2 小时)

#### 3.1 创建格式转换函数
```python
def convert_deep_research_to_standard_format(deep_research_output):
    """
    将 Deep Research 的输出转换为项目标准格式
    使用 Gemini 进行二次处理
    """
    
    conversion_prompt = f"""
    You are a content formatter. Convert the following Deep Research report into this exact format:
    
    ---START_METADATA---
    {{
      "title": "最震撼的头条标题（不超过 30 字）",
      "summary": "60-100 字的精准摘要，包含 3-4 个核心要点，用分号分隔",
      "tags": ["技术标签1", "技术标签2", "行业标签"],
      "importance": 9
    }}
    ---END_METADATA---
    
    ---START_CONTENT---
    # 💡 首席洞察 (Chief Insight)
    (综合分析今日整体局势)
    
    ## 🔥 核心情报
    
    ### 1. [情报标题]
    **来源**: [媒体名称](URL)
    - **深度拆解**: ...
    - **为何重要**: ...
    - **社区声音**: ...
    
    ### 2. [情报标题]
    ...
    
    ## 🛠️ 极客推荐
    - **[项目名](URL)**: ...
    
    ## 🔗 原始情报来源
    - [标题](URL)
    ---END_CONTENT---
    
    Original Deep Research Report:
    {deep_research_output}
    
    Requirements:
    1. Extract key information from the report
    2. Maintain all source URLs
    3. Write in Chinese (Simplified)
    4. Follow the format EXACTLY
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=conversion_prompt
    )
    
    return response.text
```

#### 3.2 测试格式一致性
- 确保生成的内容符合现有的 Notion、GitHub Issue、Email 模板
- 验证链接、日期等元数据的正确性

---

### Phase 4: 集成与测试 (预计 2 小时)

#### 4.1 更新主流程
修改 `researcher.py` 的 `main` 部分:
```python
if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("❌ 错误: GEMINI_API_KEY 未设置")
        exit(1)

    # 1. 运行 Deep Research
    try:
        raw_report = run_deep_research()
        # 将 Deep Research 输出转换为标准格式
        formatted_report = convert_deep_research_to_standard_format(raw_report)
    except Exception as e:
        print(f"⚠️ Deep Research 失败，使用降级方案: {e}")
        formatted_report = run_gemini3_research_fallback()
    
    # 2-8. 后续流程保持不变
    meta, body = parse_gemini_response(formatted_report)
    # ...
```

#### 4.2 本地测试
```bash
# 设置环境变量
export GEMINI_API_KEY="your-key"
export NOTION_TOKEN="your-token"
export NOTION_DATABASE_ID="your-db-id"

# 运行测试
python researcher.py
```

#### 4.3 验证输出
检查生成的文件:
- `docs/archives/YYYY-MM-DD.md` 格式是否正确
- Notion 同步是否成功
- GitHub Issue 是否正常发布

---

### Phase 5: 优化与监控 (预计 1-2 小时)

#### 5.1 添加性能监控
```python
import time

start_time = time.time()
raw_report = run_deep_research()
duration = time.time() - start_time

print(f"⏱️ Deep Research 耗时: {duration:.2f} 秒")
```

#### 5.2 成本估算
- Deep Research 的 API 调用成本可能高于 generate_content
- 监控每日费用，设置预算上限
- 参考: [Google AI Studio 定价](https://ai.google.dev/pricing)

#### 5.3 质量对比
- 并行运行新旧方案一周
- 对比内容深度、信息密度、用户反馈
- 决定是否完全切换

---

## 📝 实施检查清单

### 准备阶段
- [ ] 确认 Deep Research API 访问权限
- [ ] 创建测试环境分支 `feature/deep-research-migration`
- [ ] 备份当前工作代码

### 开发阶段
- [ ] 创建 `test_deep_research.py`
- [ ] 实现 `run_deep_research()`
- [ ] 实现 `convert_deep_research_to_standard_format()`
- [ ] 更新 `requirements.txt`
- [ ] 添加降级机制

### 测试阶段
- [ ] 本地运行验证
- [ ] 检查生成内容质量
- [ ] 验证所有输出渠道（Markdown, Notion, GitHub Issue, Email）
- [ ] 测试错误处理和降级逻辑

### 部署阶段
- [ ] 更新 GitHub Actions workflow（如果需要）
- [ ] 提交代码到主分支
- [ ] 监控首次自动运行
- [ ] 收集用户反馈

---

## ⚠️ 风险与应对

| 风险 | 影响 | 应对方案 |
|------|------|----------|
| Deep Research API 需要 allowlist | 高 | 提前申请访问权限；保留降级方案 |
| API 调用成本增加 | 中 | 设置成本监控；评估 ROI |
| 输出格式与预期不符 | 中 | 使用 Gemini 二次处理进行格式转换 |
| 响应时间过长（可能 5-10 分钟） | 低 | 优化 GitHub Actions timeout 设置 |
| Deep Research 返回英文报告 | 低 | 在 prompt 中强调使用中文；或二次翻译 |

---

## 📊 预期收益

### 质量提升
- **信息深度**: 从单次搜索 → 多轮深入调研
- **覆盖广度**: 自动发现更多相关来源
- **引用质量**: 结构化引用，带时间戳

### 效率提升
- **Prompt 工程**: 从复杂的手动设计 → 简洁的研究任务描述
- **维护成本**: 减少对 prompt 的频繁调整

### 用户体验
- **内容价值**: 更深入的分析和洞察
- **可信度**: 更完整的引用和来源

---

## 🔄 回滚计划

如果迁移后效果不佳，回滚步骤：
1. 恢复 `run_gemini3_research()` 为主函数
2. 移除 Deep Research 相关代码
3. 重新部署上一个稳定版本

---

## 📚 参考资源

- [Gemini Deep Research 官方文档](https://ai.google.dev/gemini-api/docs/deep-research)
- [Interactions API 文档](https://ai.google.dev/gemini-api/docs/interactions)
- [API 定价](https://ai.google.dev/pricing)
- [示例代码仓库](https://github.com/google/generative-ai-python)

---

**预计总时长**: 7-10 小时（分 2-3 天完成）

**建议开始时间**: 2025-12-29（周日）

**首次生产运行**: 2025-12-31
