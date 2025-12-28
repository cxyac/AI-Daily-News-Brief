"""
Deep Research 版本的 AI Daily News Brief 核心研究引擎
基于 Gemini Deep Research Agent (deep-research-pro-preview-12-2025)
"""

import os
import json
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from google import genai
from google.genai import types
from notion_client import Client
from github import Github

# 设置北京时区
TZ_CN = ZoneInfo("Asia/Shanghai")

# 基础配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# GitHub 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")

# 邮箱配置 (SMTP)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
NOTION_SUBSCRIBERS_DB_ID = os.getenv("NOTION_SUBSCRIBERS_DB_ID")
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT")

client = genai.Client(api_key=GEMINI_API_KEY)
notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None


def run_deep_research():
    """
    使用 Gemini Deep Research Agent 进行深度研究
    返回: 原始研究报告文本
    """
    print("🔬 正在启动 Deep Research Agent...")
    print("⏳ 预计耗时 5-15 分钟，请耐心等待...")
    
    current_date = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    yesterday = (datetime.now(TZ_CN) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 专为 Deep Research 设计的研究任务描述
    research_task = f"""
# AI Industry Intelligence Report - {current_date}

## Research Objective
You are a senior AI industry analyst tasked with creating a comprehensive daily intelligence report for AI professionals and enthusiasts. Your goal is to identify and analyze the most significant AI-related developments from the past 24 hours ({yesterday} to {current_date}).

## Research Scope

### Time Range
- Focus STRICTLY on events, news, and discussions from {yesterday} to today ({current_date})
- Verify publication dates to ensure freshness

### Coverage Areas (Equal Priority)
1. **Major Product Launches & Announcements**
   - OpenAI, Google (DeepMind), Anthropic, Meta, NVIDIA, Microsoft
   - Official blog posts, product releases, model updates
   - Sources: company blogs, press releases

2. **Academic & Technical Breakthroughs**
   - ArXiv papers with significant impact
   - HuggingFace trending models and papers
   - Novel techniques, algorithms, or architectures
   - Sources: arxiv.org, huggingface.co/papers

3. **Open Source & Developer Tools**
   - GitHub trending repositories (AI/ML category)
   - Developer tools, libraries, frameworks
   - Community-built applications
   - Sources: github.com/trending, reddit.com/r/LocalLlama, reddit.com/r/MachineLearning

4. **Industry & Business Developments**
   - Funding announcements, acquisitions, partnerships
   - Talent movement (key hires, departures)
   - Market analysis and industry trends
   - Sources: TechCrunch, VentureBeat, The Information

5. **Community Discussions & Sentiment**
   - Hot topics on Reddit (r/LocalLlama, r/MachineLearning)
   - Hacker News discussions
   - Twitter/X trending AI topics
   - Sources: news.ycombinator.com, reddit.com, twitter.com

## Search Strategy Recommendations

### Suggested Query Patterns
- `site:openai.com/blog OR site:anthropic.com OR site:deepmind.google after:YYYY-MM-DD`
- `"AI news" OR "artificial intelligence" after:{yesterday}`
- `site:techcrunch.com/category/artificial-intelligence after:{yesterday}`
- `site:arxiv.org (machine learning OR deep learning) after:{yesterday}`
- `site:github.com/trending python AI after:{yesterday}`
- `site:reddit.com/r/LocalLlama OR site:reddit.com/r/MachineLearning`
- `site:news.ycombinator.com (AI OR GPT OR LLM)`

### Source Diversity
- Aim for at least 15-20 unique sources
- Balance between official announcements and community discussions
- Verify information from multiple sources when possible

## Output Requirements

### Language
- Write the entire report in **Simplified Chinese (简体中文)**

### Structure
The report must follow this EXACT format:

---START_METADATA---
{{
  "title": "今日最震撼的头条标题（不超过30字，必须基于真实事件）",
  "summary": "60-100字的精准摘要，包含3-4个核心要点，用分号分隔",
  "tags": ["核心技术标签1", "核心技术标签2", "行业标签"],
  "importance": 8
}}
---END_METADATA---

---START_CONTENT---
# 💡 首席洞察 (Chief Insight)

（用150-200字综合分析今日AI行业的整体局势。必须基于实际发生的事件，指出趋势、关联性和潜在影响。避免空泛评论。）

## 🔥 核心情报

### 1. [具体且吸引人的标题]
**来源**: [媒体/机构名称](完整URL) | 发布时间: YYYY-MM-DD HH:MM

- **深度拆解**: （80-120字，解释核心技术、产品功能、或事件背景。避免复述新闻，要提供洞察。）

- **为何重要**: （50-80字，分析短期和长期影响。对行业、开发者、或用户意味着什么？）

- **社区声音**: （40-60字，Reddit、Hacker News、Twitter上的关键讨论点或争议。如无社区讨论则说明"社区尚未广泛讨论"。）

### 2. [另一条重要情报的标题]
...（重复上述结构）

### 3. [第三条情报]
...

### 4. [第四条情报]
...

（继续添加，确保总共有 4-6 条独立的核心情报）

## 🛠️ 极客推荐 (GitHub/Tools)

- **[项目名称](GitHub URL)**: （50-80字介绍。包含：核心功能、技术栈、为何值得关注（如Star增长、解决的痛点、独特优势等）。如有具体数据更佳，如"24小时内获得2000+ Stars"。）

- **[第二个项目名称](GitHub URL)**: ...

（至少2个，最多4个高质量开源项目）

## 🔗 原始情报来源

- [来源标题1 - 机构名称](完整URL)
- [来源标题2 - 机构名称](完整URL)
- [来源标题3 - 机构名称](完整URL)
...

（列出至少10个主要参考来源，包含所有引用的URL）

---END_CONTENT---

### Quality Standards
1. **Accuracy**: Every fact must be verifiable with a valid URL
2. **Freshness**: All events must be from the past 24 hours
3. **Depth**: Don't just summarize headlines - provide analysis and context
4. **Relevance**: Focus on high-impact news, not minor updates
5. **Completeness**: Must have 4-6 core intelligence items covering different aspects
6. **Citation**: Every claim should be backed by a source URL with publication time

### What to Avoid
- ❌ Generic commentary without specific events
- ❌ Outdated news (older than 24 hours)
- ❌ Speculation without evidence
- ❌ Repeating the same information multiple times
- ❌ Including only 1-2 news items (must have 4-6)

## Target Audience
AI professionals, developers, researchers, and enthusiasts who need:
- High signal-to-noise ratio
- Deep technical understanding
- Actionable insights
- Time savings (they don't want to browse 20 sites daily)

## Your Mission
Act as their personal AI intelligence officer. Spend the necessary time to thoroughly research, verify, and synthesize the most important AI developments of the day. Quality over speed.
    """
    
    try:
        start_time = time.time()
        
        # 创建后台研究任务
        interaction = client.interactions.create(
            input=research_task,
            agent='deep-research-pro-preview-12-2025',
            background=True  # 异步执行，因为可能需要 5-20 分钟
        )
        
        print(f"✅ 研究任务已启动: {interaction.id}")
        print("📊 任务状态监控中...")
        
        # 轮询检查任务状态
        poll_count = 0
        while True:
            poll_count += 1
            interaction = client.interactions.get(interaction.id)
            
            status = interaction.status
            
            if status == "completed":
                elapsed = time.time() - start_time
                print(f"✅ 研究完成！耗时: {elapsed/60:.1f} 分钟")
                
                # 获取最终输出
                if interaction.outputs and len(interaction.outputs) > 0:
                    result = interaction.outputs[-1].text
                    print(f"📝 报告长度: {len(result)} 字符")
                    return result
                else:
                    raise Exception("研究完成但无输出内容")
                    
            elif status == "failed":
                error_msg = getattr(interaction, 'error', '未知错误')
                raise Exception(f"研究任务失败: {error_msg}")
                
            else:
                # 正在进行中
                elapsed = time.time() - start_time
                print(f"⏳ [{poll_count}] 状态: {status} | 已耗时: {elapsed/60:.1f} 分钟")
                
                # 每 30 秒检查一次
                time.sleep(30)
                
                # 超时保护（最多等待 60 分钟）
                if elapsed > 3600:
                    raise Exception("任务超时（超过60分钟）")
                    
    except Exception as e:
        print(f"❌ Deep Research 执行失败: {e}")
        raise


def run_gemini3_research_fallback():
    """
    降级方案：使用原有的 generate_content 方式
    当 Deep Research 不可用或失败时使用
    """
    print("🔄 使用降级方案: Gemini 3 Pro generate_content")
    
    current_date = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    yesterday = (datetime.now(TZ_CN) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    mode_instruction = "重点关注：OpenAI, Google, Anthropic, 英伟达, Meta 等巨头的最新发布和新闻。以及 ArXiv 上的突破性论文。"

    prompt = f"""
    # 角色定义
    你是一位站在 AI 行业最前沿的【首席情报官】，擅长从海量碎片信息(包括新闻、论文、社区讨论)中提取最有价值的洞察。
    
    # 时效与环境
    今天是 {current_date}。
    你的搜索范围是 {yesterday} 至今。
    {mode_instruction}
    
    # 你的目标
    为订阅者提供一份**"高信噪比、多维度"**的情报。
    **不要**只列出 1-2 条新闻，请确保报告包含 **4-6 个** 独立且有深度的情报点。优先级：真实性 > 新鲜度 > 完整性
    如果官方新闻很少，请挖掘社区(Reddit/HN/Twitter)的热门议题。

    # 深度研究任务 (必须覆盖以下维度)
    1. **️🔥 头条聚焦**：过去 24h 影响最大的事件 (可以是发布、也可以是争议/讨论)。
    2. **🧪 学术与技术**：ArXiv 热门论文 或 HuggingFace 上的新晋 SOTA 模型。
    3. **🛠️ 开源与黑客**：GitHub Trending 或 Reddit 上被开发者热议的实战工具/Trick。
    4. **📉 商业与风向**：融资、人才流动或行业分析。
    
    # 搜索策略 (多样化)
    - 官方源：`site:openai.com/blog`, `site:anthropic.com`
    - 资讯源：`AI news after:{yesterday}`, `VentureBeat AI`, `TechCrunch AI`
    - 社区源：`site:reddit.com/r/LocalLlama top 24h`, `site:news.ycombinator.com AI`, `site:huggingface.co/papers`
    
    # 输出要求 (Markdown + JSON)
    你的输出必须包含【思考过程】并严格遵守以下格式：
    
    ---START_METADATA---
    {{
      "title": "今日最有震撼力的头条标题（不超过 30 字）",
      "summary": "60-100 字的精准摘要，必须包含 3-4 个核心要点，每个要点用分号分隔",
      "tags": ["核心技术标签","核心技术标签2", "行业标签"],
      "importance": 9
    }}
    ---END_METADATA---
    
    ---START_CONTENT---
    # 💡 首席洞察 (Chief Insight)
    (用一段话合成今日的整体局势。必须基于真实发生的事件，避免空泛评论)
    
    ## 🔥 核心情报 (4-6条)
    
    ### 1. [情报标题]
    **来源**: [媒体/社区名称](URL) | 发布时间
    
    - **深度拆解**: (50-100字，核心技术或事件脉络)
    
    - **为何重要**: (一句话点出说明对行业的短期和长期影响。)
    
    - **社区声音**: (Reddit、Hacker News、Twitter 上的关键争议或好评)
    
    ### 2. [情报标题]
    ...
    
    ### 3. [情报标题]
    ...
    
    ## 🛠️ 极客推荐 (GitHub/Tools)
    - **[项目名](URL)**: (一句话介绍核心功能 + 为什么值得关注（如：Star 数增长、解决的痛点等）)
    
    ## 🔗 原始情报来源
    - [标题](URL)
    ---END_CONTENT---
    """

    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',  # 使用更稳定的模型
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )
    )
    return response.text


def parse_gemini_response(raw_text):
    """从原始文本中提取元数据和正文内容"""
    try:
        metadata_match = re.search(r'---START_METADATA---(.*?)---END_METADATA---', raw_text, re.DOTALL)
        content_match = re.search(r'---START_CONTENT---(.*?)---END_CONTENT---', raw_text, re.DOTALL)
        
        if metadata_match and content_match:
            json_str = metadata_match.group(1).strip()
            # 清理 JSON 中可能包裹的 markdown 代码块标识
            json_str = re.sub(r'^```json|```$', '', json_str, flags=re.MULTILINE).strip()
            metadata = json.loads(json_str)
            content = content_match.group(1).strip()
            return metadata, content
        else:
            # 如果没有找到标记，尝试用 AI 重新格式化
            print("⚠️ 未找到标准格式标记，尝试使用 AI 重新格式化...")
            return reformat_with_ai(raw_text)
    except Exception as e:
        print(f"⚠️ 解析出错: {e}")
        return None, raw_text


def reformat_with_ai(raw_report):
    """
    使用 Gemini 将非标准格式的报告转换为标准格式
    这是一个保险措施，确保即使 Deep Research 输出格式不符也能处理
    """
    print("🔄 正在使用 AI 重新格式化报告...")
    
    conversion_prompt = f"""
你是一个内容格式化专家。请将以下 AI 研究报告转换为指定的标准格式。

要求：
1. 提取所有关键信息
2. 保留所有来源 URL 和时间
3. 使用简体中文
4. 严格遵守输出格式

输出格式：
---START_METADATA---
{{
  "title": "最震撼的头条标题（不超过30字）",
  "summary": "60-100字的摘要，包含3-4个要点，用分号分隔",
  "tags": ["标签1", "标签2", "标签3"],
  "importance": 8
}}
---END_METADATA---

---START_CONTENT---
# 💡 首席洞察
（综合分析段落）

## 🔥 核心情报

### 1. [标题]
**来源**: [名称](URL) | 时间

- **深度拆解**: ...
- **为何重要**: ...
- **社区声音**: ...

（继续其他情报项...）

## 🛠️ 极客推荐
- **[项目](URL)**: ...

## 🔗 原始情报来源
- [标题](URL)
---END_CONTENT---

原始报告：
{raw_report}
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=conversion_prompt
        )
        
        formatted_text = response.text
        return parse_gemini_response(formatted_text)
        
    except Exception as e:
        print(f"❌ AI 重新格式化失败: {e}")
        # 返回基本的元数据和原始内容
        default_meta = {
            "title": f"AI 深度简报 - {datetime.now(TZ_CN).strftime('%Y-%m-%d')}",
            "summary": "今日 AI 行业情报已送达",
            "tags": ["AI", "深度研究"],
            "importance": 7
        }
        return default_meta, raw_report


# 以下函数与原版 researcher.py 相同，直接复用
# 包括: split_content_to_blocks, save_to_notion, update_archive_index, 
# update_homepage, save_to_markdown_file, publish_to_github_issue, send_email_newsletter

# [此处省略这些函数的代码，在实际使用时从原文件复制过来]


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("❌ 错误: GEMINI_API_KEY 未设置")
        exit(1)

    print("="*60)
    print("🤖 AI Daily News Brief - Deep Research Edition")
    print("="*60)
    
    # 1. 运行 Deep Research（带降级机制）
    try:
        raw_report = run_deep_research()
        print("\n✅ Deep Research 执行成功")
    except Exception as e:
        print(f"\n⚠️ Deep Research 失败，使用降级方案: {e}")
        try:
            raw_report = run_gemini3_research_fallback()
            print("\n✅ 降级方案执行成功")
        except Exception as e2:
            print(f"\n❌ 降级方案也失败了: {e2}")
            exit(1)
    
    # 2. 解析内容（自动处理格式转换）
    meta, body = parse_gemini_response(raw_report)
    if not meta:
        meta = {
            "title": f"AI 深度简报 - {datetime.now(TZ_CN).strftime('%Y-%m-%d')}",
            "summary": "今日情报已送达",
            "tags": ["AI", "每日简报"]
        }
    
    print(f"\n📋 报告标题: {meta.get('title')}")
    print(f"📊 报告长度: {len(body)} 字符")
    
    # 3-8. 后续流程与原版相同
    # [此处需要复制原 researcher.py 的步骤 3-8]
    
    print("\n" + "="*60)
    print("🎉 所有任务完成！")
    print("="*60)
