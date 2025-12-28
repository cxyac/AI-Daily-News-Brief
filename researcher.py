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

# 1. 基础配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# GitHub 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")  # 格式: "username/repo"

# 邮箱配置 (SMTP)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
NOTION_SUBSCRIBERS_DB_ID = os.getenv("NOTION_SUBSCRIBERS_DB_ID")
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT")

client = genai.Client(api_key=GEMINI_API_KEY)
notion = Client(auth=NOTION_TOKEN)

def send_email_newsletter(metadata, markdown_content):
    """通过 SMTP 发送 HTML 格式的简报邮件"""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        return

    print("📧 正在启动 SMTP 邮件推送...")
    
    recipients = []
    if TEST_RECIPIENT:
        print(f"🧪 测试模式: 仅发送给 {TEST_RECIPIENT}")
        recipients.append(TEST_RECIPIENT)
    elif NOTION_SUBSCRIBERS_DB_ID and notion:
        print("👥 正在从 Notion 读取订阅者列表...")
        try:
            # 查询 Notion 数据库 (分页获取所有用户)
            has_more = True
            start_cursor = None
            
            while has_more:
                # 使用 Notion API 2025 (Data Sources)
                query_kwargs = {
                    "data_source_id": NOTION_SUBSCRIBERS_DB_ID,
                    "page_size": 100
                }
                if start_cursor:
                    query_kwargs["start_cursor"] = start_cursor
                
                resp = notion.data_sources.query(**query_kwargs)
                
                for page in resp.get("results", []):
                    props = page.get("properties", {})
                    email = ""
                    # 尝试寻找常见的邮箱列名 (Email, 邮箱, Mail)
                    for key, val in props.items():
                        if "mail" in key.lower() or "邮箱" in key:
                            # 根据 Notion 字段类型提取文本
                            if val["type"] == "email":
                                email = val["email"]
                            elif val["type"] == "rich_text" and val["rich_text"]:
                                email = val["rich_text"][0]["text"]["content"]
                            elif val["type"] == "title" and val["title"]:
                                email = val["title"][0]["text"]["content"]
                            break
                    
                    if email and "@" in email:
                        recipients.append(email.strip())
                
                has_more = resp.get("has_more")
                start_cursor = resp.get("next_cursor")
                
            # 去重
            recipients = list(set(recipients))
            print(f"👥 共获取到 {len(recipients)} 位订阅者")
            
        except Exception as e:
            print(f"❌ 读取 Notion 订阅列表失败: {e}")
    
    if not recipients:
        print("⚠️ 没有收件人 (请配置 TEST_RECIPIENT 或 检查 Notion 连接)，跳过发送")
        return

    # 将 Markdown 转换为 HTML
    html_body = markdown.markdown(markdown_content)
    
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            h2 {{ color: #333; margin-top: 30px; }}
            a {{ color: #007bff; text-decoration: none; }}
            blockquote {{ border-left: 4px solid #007bff; margin: 0; padding-left: 15px; color: #555; background: #f9f9f9; padding: 10px; }}
        </style>
    </head>
    <body>
        <div style="text-align: center; margin-bottom: 20px;">
            <p>👇 点击下方链接查看完整排版 👇</p>
            <a href="{os.getenv('mkdocs_site_url', 'https://news.helloaidev.com')}" style="background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">在浏览器中阅读</a>
        </div>
        {html_body}
        <div style="margin-top: 40px; font-size: 12px; color: #888; text-align: center;">
            <p>本邮件由 AI Daily News Brief 自动发送</p>
        </div>
    </body>
    </html>
    """

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        for email_addr in recipients:
            msg = MIMEMultipart()
            msg['From'] = f"AI Daily Brief <{EMAIL_USER}>"
            msg['To'] = email_addr
            date_str = datetime.now(TZ_CN).strftime('%Y-%m-%d')
            msg['Subject'] = f"🤖 {metadata.get('title')} ({date_str})"
            msg.attach(MIMEText(full_html, 'html'))
            server.send_message(msg)
            print(f"✅ 邮件已发送至: {email_addr}")
            
        server.quit()
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

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

2. **Academic & Technical Breakthroughs**
   - ArXiv papers with significant impact
   - HuggingFace trending models and papers

3. **Open Source & Developer Tools**
   - GitHub trending repositories (AI/ML category)
   - Developer tools, libraries, frameworks

4. **Industry & Business Developments**
   - Funding announcements, acquisitions, partnerships
   - Market analysis and industry trends

5. **Community Discussions & Sentiment**
   - Hot topics on Reddit (r/LocalLlama, r/MachineLearning)
   - Hacker News discussions

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
**来源**: [媒体/机构名称](完整URL) | 发布时间: YYYY-MM-DD

- **深度拆解**: （80-120字，解释核心技术、产品功能、或事件背景。避免复述新闻，要提供洞察。）

- **为何重要**: （50-80字，分析短期和长期影响。）

- **社区声音**: （40-60字，Reddit、Hacker News、Twitter上的关键讨论点。）

### 2. [另一条重要情报的标题]
...

（继续添加，确保总共有 4-6 条独立的核心情报）

## 🛠️ 极客推荐 (GitHub/Tools)

- **[项目名称](GitHub URL)**: （50-80字介绍核心功能和为何值得关注）

（至少2个，最多4个高质量开源项目）

## 🔗 原始情报来源

- [来源标题1 - 机构名称](完整URL)
...

（列出至少10个主要参考来源）

---END_CONTENT---

### Quality Standards
1. **Accuracy**: Every fact must be verifiable with a valid URL
2. **Freshness**: All events must be from the past 24 hours
3. **Depth**: Don't just summarize headlines - provide analysis and context
4. **Completeness**: Must have 4-6 core intelligence items covering different aspects

## Your Mission
Act as their personal AI intelligence officer. Spend the necessary time to thoroughly research, verify, and synthesize the most important AI developments of the day. Quality over speed.
    """
    
    try:
        start_time = time.time()
        
        # 创建后台研究任务
        interaction = client.interactions.create(
            input=research_task,
            agent='deep-research-pro-preview-12-2025',
            background=True
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
                elapsed = time.time() - start_time
                print(f"⏳ [{poll_count}] 状态: {status} | 已耗时: {elapsed/60:.1f} 分钟")
                time.sleep(30)
                
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
    print("🔄 使用降级方案: Gemini generate_content")
    
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
        model='gemini-3-pro-preview',  # 使用与原版相同的模型
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            thinking_config=types.ThinkingConfig(include_thoughts=True)  # 启用思考模式
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
            return None, raw_text
    except Exception as e:
        print(f"⚠️ 解析解析出错: {e}")
        return None, raw_text

def split_content_to_blocks(text):
    """
    将 Markdown 文本转换为 Notion 的结构化 Block
    支持：Heading 1/2/3, Bullet List, Quote, Paragraph
    """
    blocks = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line: 
            continue
        
        # 1. Heading 1 (# )
        if line.startswith('# '):
            content = line[2:].strip()[:2000]
            blocks.append({
                "object": "block", "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": content}}]}
            })
        # 2. Heading 2 (## )
        elif line.startswith('## '):
            content = line[3:].strip()[:2000]
            blocks.append({
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": content}}]}
            })
        # 3. Heading 3 (### )
        elif line.startswith('### '):
            content = line[4:].strip()[:2000]
            blocks.append({
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": content}}]}
            })
        # 4. Bullet List (- or * )
        elif line.startswith('- ') or line.startswith('* '):
            content = line[2:].strip()[:2000]
            blocks.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": content}}]}
            })
        # 5. Quote (> )
        elif line.startswith('> '):
            content = line[2:].strip()[:2000]
            blocks.append({
                "object": "block", "type": "quote",
                "quote": {"rich_text": [{"text": {"content": content}}]}
            })
        # 6. Default Paragraph
        else:
            # Notion block character limit is 2000
            content = line[:2000]
            blocks.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": content}}]}
            })
            
    return blocks

def save_to_notion(metadata, content):
    """将已解析的内容同步到 Notion"""
    print("📓 正在同步至 Notion...")
    try:
        # 获取当前日期（北京时间）
        publish_date = datetime.now(TZ_CN).strftime('%Y-%m-%d')
        
        body_blocks = split_content_to_blocks(content)
        
        # 构建 properties，包括发布日期
        properties = {
            "标题": {"title": [{"text": {"content": metadata.get('title', '今日 AI 简报')}}]},
            "一句话摘要": {"rich_text": [{"text": {"content": metadata.get('summary', '')}}]},
            "核心领域": {"multi_select": [{"name": tag} for tag in metadata.get('tags', []) if tag]},
            "发布日期": {"date": {"start": publish_date}}
        }
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties,
            children=body_blocks[:100] 
        )
        print(f"✅ Notion 同步成功！发布日期: {publish_date}")
    except Exception as e:
        print(f"❌ Notion 保存失败: {e}")

def update_archive_index(archive_dir):
    """遍历文件夹，生成归档列表"""
    # 确保目录存在
    if not os.path.exists(archive_dir):
        print(f"⚠️ 目录 {archive_dir} 不存在，跳过索引更新")
        return

    files = [f for f in os.listdir(archive_dir) if f.endswith(".md") and f != "index.md"]
    files.sort(reverse=True) # 按日期倒序排
    
    index_path = os.path.join(archive_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# 📅 日报归档\n\n")
        f.write("点击下方日期查看当天的 AI 深度研究：\n\n")
        for file in files:
            date_name = file.replace(".md", "")
            f.write(f"- [{date_name} 的 AI 简报]({file})\n")
    print(f"✅ 归档索引已同步更新至: {index_path}")

def update_homepage(metadata, content):
    """动态更新首页 index.md，展示最新简报预览"""
    print("🏠 正在更新首页动态内容...")
    date_str = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    
    # 1. 构造首页内容
    # 我们只取正文的前 600 个字符作为预览，避免首页过长
    preview_content = content[:600] + "..." if len(content) > 600 else content
    
    homepage_template = f"""# 🤖 AI 每日深度研究简报

> **最新动态 ({date_str})**: {metadata.get('summary')}

## 🌟 今日头条: {metadata.get('title')}

{preview_content}

---

### 🔗 快速链接
- [📅 查看完整报告](archives/{date_str}.md)
- [📚 往期内容归档](archives/index.md)

### 🛠️ 订阅说明
本站点由 **Gemini 3 Pro** 驱动，每日早 8 点通过 **GitHub Actions** 自动深度搜索全网 AI 情报并更新。

<iframe data-tally-src="https://tally.so/embed/kd9P9J?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1" loading="lazy" width="100%" height="200" frameborder="0" marginheight="0" marginwidth="0" title="subscribe"></iframe>
<script>var d=document,w="https://tally.so/widgets/embed.js",v=function(){{"undefined"!=typeof Tally?Tally.loadEmbeds():d.querySelectorAll("iframe[data-tally-src]:not([src])").forEach((function(e){{e.src=e.dataset.tallySrc}}))}};if("undefined"!=typeof Tally)v();else if(d.querySelector('script[src="'+w+'"]')==null){{var s=d.createElement("script");s.src=w,s.onload=v,s.onerror=v,d.body.appendChild(s);}}</script>

---
*上次更新时间：{datetime.now(TZ_CN).strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # 2. 写入 docs/index.md
    with open("docs/index.md", "w", encoding="utf-8") as f:
        f.write(homepage_template)
    print("✅ 首页已更新为最新内容")


def save_to_markdown_file(metadata, content):
    """将内容保存为 Markdown 文件，供 MkDocs 使用"""
    date_str = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    print(f"🌐 正在生成网页文件: {date_str}.md")
    
    # 确保目录存在
    save_dir = "docs/archives"
    os.makedirs(save_dir, exist_ok=True)
    file_path = f"{save_dir}/{date_str}.md"
    
    # 构造带有 Front Matter 的内容，这有利于 MkDocs 的 SEO 和页面显示
    full_markdown = f"""---
title: {metadata.get('title')}
date: {date_str}
tags: {metadata.get('tags', [])}
description: {metadata.get('summary')}
---

# {metadata.get('title')}

> **摘要**: {metadata.get('summary')}

{content}

<div class="subscribe-card">
    <div class="subscribe-title">📩 订阅每日 AI 简报</div>
    <div class="subscribe-desc">每天早晨，将最新的 AI 突破与深度洞察直接发送到您的收件箱。</div>
<iframe data-tally-src="https://tally.so/embed/kd9P9J?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1" loading="lazy" width="100%" height="200" frameborder="0" marginheight="0" marginwidth="0" title="subscribe"></iframe>
<script>var d=document,w="https://tally.so/widgets/embed.js",v=function(){{"undefined"!=typeof Tally?Tally.loadEmbeds():d.querySelectorAll("iframe[data-tally-src]:not([src])").forEach((function(e){{e.src=e.dataset.tallySrc}}))}};if("undefined"!=typeof Tally)v();else if(d.querySelector('script[src="'+w+'"]')==null){{var s=d.createElement("script");s.src=w,s.onload=v,s.onerror=v,d.body.appendChild(s);}}</script>
    <div style="margin-top: 10px; font-size: 0.8em; opacity: 0.7;">或者回复 GitHub Issue 进行评论互动</div>
</div>

---
*生成时间：{datetime.now(TZ_CN).strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)
    print(f"✅ 网页文件已保存至: {file_path}")

def publish_to_github_issue(metadata, content):
    """将简报发布为您 GitHub 仓库的 Issue，实现邮件推送订阅"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("⚠️ 未配置 GITHUB_TOKEN 或 GITHUB_REPOSITORY，跳过 Issue 发布")
        return

    print("📧 正在发布 GitHub Issue...")
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        # 构造 Issue 标题和正文
        date_str = datetime.now(TZ_CN).strftime('%Y-%m-%d')
        issue_title = f"{date_str} | {metadata.get('title')}"
        
        # 在正文顶部加上原文链接，增加导流
        issue_body = f"""
> **摘要**: {metadata.get('summary')}

[👉 点击查看完整排版报告](https://cxyac.github.io/AI-Daily-News-Brief/archives/{date_str}/)

---

{content}

---
*本报告由 AI Agent 自动生成，回复本 Issue 可参与讨论。*
"""
        repo.create_issue(title=issue_title, body=issue_body, labels=["daily-brief"])
        print(f"✅ GitHub Issue 已发布：{issue_title}")
    except Exception as e:
        print(f"❌ GitHub Issue 发布失败: {e}")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("❌ 错误: GEMINI_API_KEY 未设置")
        exit(1)

    print("="*70)
    print("🤖 AI Daily News Brief - Deep Research Edition")
    print("="*70)

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
    
    # 2. 解析内容
    meta, body = parse_gemini_response(raw_report)
    if not meta:
        meta = {"title": f"AI 深度简报 - {datetime.now(TZ_CN).strftime('%Y-%m-%d')}", "summary": "今日情报已送达", "tags": ["AI"]}

    print(f"\n📋 报告标题: {meta.get('title')}")
    print(f"📊 报告长度: {len(body)} 字符")

    # 3. 存储当天详情页 (.md 文件)
    save_to_markdown_file(meta, body) 

    # 4. 更新"索引目录" (让 Archives 页面出现新链接)
    update_archive_index("docs/archives") 

    # 5. 更新"网站首页" (让首页展示今天的预览)
    update_homepage(meta, body)

    # 6. 同步 Notion (可选备份)
    if NOTION_TOKEN and DATABASE_ID:
        save_to_notion(meta, body)

    # 7. 发布 GitHub Issue (作为邮件订阅渠道)
    publish_to_github_issue(meta, body)

    # 8. SMTP 邮件推送
    send_email_newsletter(meta, body)

    print("\n" + "="*70)
    print("🎉 所有任务完成！")
    print("="*70)