import os
import json
import re
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

def run_gemini3_research():
    """使用 Gemini 3 Pro 进行每日动态深度研究"""
    print("🚀 正在启动 Gemini 3 Pro 深度研究引擎...")
    
    current_date = datetime.now(TZ_CN).strftime('%Y-%m-%d')
    # 动态获取昨天的日期
    yesterday = (datetime.now(TZ_CN) - timedelta(days=1)).strftime('%Y-%m-%d')

    
    # 判断是否为周末 (5=Saturday, 6=Sunday)
    is_weekend = datetime.now(TZ_CN).weekday() >= 5
    mode_instruction = ""
    if is_weekend:
        mode_instruction = """
        【周末特别模式】
        今天是周末，大厂官方新闻可能较少。请将搜索重心转移到：
        1. **深度技术帖**：Reddit (r/LocalLlama, r/MachineLearning) 或 Hacker News 上的高热度技术讨论。
        2. **GitHub 书签**：本周内新发布但被忽视的“宝藏”开源项目。
        3. **实战教程**：Twitter/X 上大佬分享的最新模型微调 (Fine-tuning) 或 RAG 最佳实践。
        不要受限于“突发新闻”，寻找那些“值得开发者花周末时间研究”的内容。
        """
    else:
        mode_instruction = "重点关注：OpenAI, Google, Anthropic 等巨头的最新发布和 ArXiv 上的突破性论文。"

    # 获取当前年份用于验证
    current_year = datetime.now(TZ_CN).year
    
    prompt = f"""
    # ⚠️⚠️⚠️ 时间验证警告 ⚠️⚠️⚠️
    
    当前年份：**{current_year} 年**（不是 2024 年！）
    今天完整日期：**{current_date}**（北京时间）
    
    **严禁使用 2024 年或更早的信息！** 
    所有日期必须是 {current_year} 年的，格式：{current_year}-MM-DD
    
    # 角色定义
    你是一位站在 AI 行业最前沿的【首席情报官】，擅长从海量碎片信息(包括新闻、论文、社区讨论)中提取最有价值的洞察。
    
    # ⚠️ 关键约束：时效性是第一优先级
    今天是 {current_date}（{current_year} 年，北京时间）。
    你的搜索范围：**{yesterday} 至 {current_date}**（最近 24 小时）
    
    **严格要求**：
    1. 只报道发生在 {current_year} 年的信息
    2. 每个情报的时间必须标注为：{current_year}-MM-DD 格式
    3. 如果搜索结果显示是 2024 年的，立即丢弃
    4. 无法确认年份的信息，直接丢弃
    5. 优先级：真实性 > 新鲜度 > 完整性
    6. 优先使用英文来源，英文信息优先于中文
    
    {mode_instruction}
    
    # 你的核心任务
    为订阅者提供一份**"高信噪比、多维度、可验证"**的情报简报。
    
    **数量要求（强制）**：
    - 核心情报：至少 **4 条**，最多 6 条
    - 每条情报必须包含：标题、来源、日期、深度分析
    - 极客推荐：至少 **2 个** GitHub 项目或工具
    - 原始来源链接：至少 **5 个** 可验证的 URL
    
    # 深度研究维度（按优先级排序）
    
    ## 第一层：官方发布与突发事件（最高优先级）
    - OpenAI, Anthropic, Google DeepMind, Meta AI 的官方博客
    - 大模型版本更新、API 变更、定价调整
    - 重大收购、融资、人事变动
    
    **搜索指令**：
    ```
    site:openai.com/blog OR site:anthropic.com OR site:deepmind.google after:{yesterday}
    "GPT" OR "Claude" OR "Gemini" after:{yesterday}
    "AI announcement" after:{yesterday}
    ```
    
    ## 第二层：学术前沿（过去 24h 的论文）
    - ArXiv cs.AI, cs.CL, cs.LG 分类下的新论文
    - HuggingFace Papers 的 Trending
    - Reddit r/MachineLearning 的热门讨论
    
    **搜索指令**：
    ```
    site:arxiv.org after:{yesterday} (LLM OR "large language model" OR GPT OR transformer)
    site:huggingface.co/papers after:{yesterday}
    site:reddit.com/r/MachineLearning top this week
    ```
    
    ## 第三层：开发者社区与实战工具
    - GitHub Trending (AI/ML 分类)
    - Reddit r/LocalLlama 的热门项目
    - Hacker News 首页关于 AI 的讨论
    
    **搜索指令**：
    ```
    site:github.com/trending/python after:{yesterday}
    site:reddit.com/r/LocalLlama top today
    site:news.ycombinator.com "AI" OR "LLM" after:{yesterday}
    ```
    
    ## 第四层：行业动态与分析
    - VentureBeat, TechCrunch, The Verge 的 AI 报道
    - 行业分析师的观点（a16z, Sequoia 等）
    
    **搜索指令**：
    ```
    site:venturebeat.com/ai OR site:techcrunch.com/tag/artificial-intelligence after:{yesterday}
    "AI funding" OR "AI startup" after:{yesterday}
    ```
    
    # 信息验证清单（每条情报必须通过）
    ✅ 能找到原始来源链接
    ✅ 信息发布时间在过去 24h 内
    ✅ 至少有 2 个独立来源确认（对于重大新闻）
    ✅ 避免模糊的时间表述（如"最近"、"不久前"）
    
    # 输出格式要求（严格遵守）
    
    ---START_METADATA---
    {{
      "title": "今日最有震撼力的头条标题（不超过 30 字）",
      "summary": "60-100 字的精准摘要，必须包含 3-4 个核心要点，每个要点用分号分隔",
      "tags": ["核心技术标签1", "核心技术标签2", "行业标签"],
      "importance": 7,
      "date": "{current_date}"
    }}
    ---END_METADATA---
    
    ---START_CONTENT---
    # 💡 首席洞察 (Chief Insight)
    （用 2-3 句话总结今日整体局势。必须基于真实发生的事件，避免空泛评论）
    
    ## 🔥 核心情报（4-6 条）
    
    ### 1. [具体事件标题 - 必须包含关键实体名称]
    **来源**: [媒体名称 + 原文链接]  
    **时间**: {current_year}-MM-DD（必须包含年份！格式示例：{current_date}）
    
    - **深度拆解**: 
      用 80-150 字说明：这是什么？为什么发生？核心技术/商业逻辑是什么？
      必须包含具体数字、版本号、技术细节等可验证信息。
    
    - **为何重要**: 
      一句话（30-50 字）说明对行业的短期和长期影响。
    
    - **社区反馈**: 
      Reddit、Hacker News、Twitter 上的真实评论摘录（如有）。
      如果没有社区讨论，说明"暂无广泛讨论"。
    
    ### 2. [第二条情报...]
    （格式同上）
    
    ### 3. [第三条情报...]
    （格式同上）
    
    ### 4. [第四条情报...]
    （格式同上）
    
    （如果有第 5、6 条，继续添加）
    
    ## 🛠️ 极客推荐（至少 2 个）
    - **[项目完整名称](完整 GitHub URL)**: 
      一句话介绍核心功能 + 为什么值得关注（如：Star 数增长、解决的痛点等）
      发布/更新时间：{yesterday} 或 {current_date}
    
    - **[项目2](URL)**: ...
    
    ## 🔗 原始情报来源（至少 5 个）
    - [具体标题1](完整 URL) - 发布时间
    - [具体标题2](完整 URL) - 发布时间
    - [具体标题3](完整 URL) - 发布时间
    - [具体标题4](完整 URL) - 发布时间
    - [具体标题5](完整 URL) - 发布时间
    
    ---END_CONTENT---
    
    # 最后提醒
    - 宁缺毋滥：如果某个维度真的没有重要信息，诚实说明"今日无重大更新"
    - 避免臆测：所有分析必须基于已发生的事实
    - 链接必须真实：不要编造 URL，如果找不到链接就说明信息来源
    - 时间精确：每条情报必须标注确切日期，格式为 YYYY-MM-DD
    """

    response = client.models.generate_content(
        model='gemini-3-pro-preview', 
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    
    # 日期验证与清理
    generated_text = response.text
    current_year = datetime.now(TZ_CN).year
    
    # 检查是否包含错误年份
    if "2024" in generated_text or "2023" in generated_text:
        print(f"⚠️  警告：生成的内容包含旧年份数据，正在尝试修正...")
        
        # 替换错误的年份（保守处理）
        import re
        # 替换日期格式中的 2024 为当前年份
        generated_text = re.sub(r'\b2024-(\d{2})-(\d{2})\b', f'{current_year}-\\1-\\2', generated_text)
        generated_text = re.sub(r'\b2023-(\d{2})-(\d{2})\b', f'{current_year}-\\1-\\2', generated_text)
        
        # 替换文本中的年份提及
        generated_text = re.sub(r'\b2024\s*年', f'{current_year} 年', generated_text)
        generated_text = re.sub(r'\b2023\s*年', f'{current_year} 年', generated_text)
        
        print(f"✅ 已将内容中的年份修正为 {current_year} 年")
    else:
        print(f"✅ 日期验证通过：未发现旧年份数据")
    
    return generated_text

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

    # 1. 运行 AI 研究
    raw_report = run_gemini3_research()
    
    # 2. 解析内容
    meta, body = parse_gemini_response(raw_report)
    if not meta:
        meta = {"title": f"AI 深度简报 - {datetime.now(TZ_CN).strftime('%Y-%m-%d')}", "summary": "今日情报已送达", "tags": ["AI"]}

    # 3. 存储当天详情页 (.md 文件)
    save_to_markdown_file(meta, body) 

    # 4. 更新“索引目录” (让 Archives 页面出现新链接)
    update_archive_index("docs/archives") 

    # 5. 更新“网站首页” (让首页展示今天的预览)
    update_homepage(meta, body)

    # 6. 同步 Notion (可选备份)
    if NOTION_TOKEN and DATABASE_ID:
        save_to_notion(meta, body)

    # 7. 发布 GitHub Issue (作为邮件订阅渠道)
    publish_to_github_issue(meta, body)

    # 8. SMTP 邮件推送 (新增)
    send_email_newsletter(meta, body)