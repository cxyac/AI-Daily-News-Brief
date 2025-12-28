# 🤖 AI Daily News Brief

> 由 **Gemini 3 Pro** 驱动的全自动 AI 每日深度简报  
> 每天早晨 8 点，自动聚合过去 24 小时全球 AI 领域的热点新闻、前沿论文与开源项目

[![Website](https://img.shields.io/badge/📰_在线阅读-news.helloaidev.com-blue?style=for-the-badge)](https://news.helloaidev.com)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/cxyac/AI-Daily-News-Brief/daily_ai.yml?style=for-the-badge&label=每日更新)](https://github.com/cxyac/AI-Daily-News-Brief/actions)
[![License](https://img.shields.io/github/license/cxyac/AI-Daily-News-Brief?style=for-the-badge)](./LICENSE)

---

## ✨ 项目特色

### 🎯 **智能过滤，拒绝噪音**
- 不是简单的新闻聚合，而是由 AI 首席情报官进行**深度拆解**和**趋势预判**
- 严格的时效性验证：只报道**过去 24 小时**发生的事件
- 多维度覆盖：官方发布、学术前沿、开源项目、行业动态

### 🔄 **全自动运作**
```
GitHub Actions 定时触发 
  → Gemini 3 Pro 深度搜索（Google Search Grounding）
  → 结构化内容生成
  → 同步至 Notion 数据库
  → 发布为 GitHub Issue
  → SMTP 邮件推送给订阅者
  → 部署到 MkDocs 静态网站
```

### 📬 **多端同步**
- 🌐 **网页版**：[news.helloaidev.com](https://news.helloaidev.com) - 精美排版，适合沉浸式阅读
- 📧 **邮件推送**：订阅后每天早晨自动送达收件箱
- 📓 **Notion 同步**：自动备份到 Notion 数据库（含标签、摘要）
- 💬 **GitHub Issue**：支持评论互动

---

## 📮 如何订阅？

### 方式 1：邮件订阅（推荐）
访问 [官网订阅页面](https://news.helloaidev.com) 或点击下方按钮：

<a href="https://tally.so/r/kd9P9J" target="_blank">
  <img src="https://img.shields.io/badge/📧_邮件订阅-立即订阅-success?style=for-the-badge" alt="邮件订阅">
</a>

### 方式 2：GitHub Issue 通知
1. 点击右上角的 **Watch** 按钮
2. 选择 **Custom** → 勾选 **Issues**
3. 每天简报发布为 Issue 时，GitHub 会推送通知

### 方式 3：RSS 订阅
添加以下 RSS 源到你的阅读器：
```
https://cxyac.github.io/AI-Daily-News-Brief/feed_rss_created.xml
```

---

## 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| **AI 引擎** | Google Gemini 3 Pro | 智能搜索与内容生成 |
| **搜索增强** | Grounding (Google Search) | 实时网络信息检索 |
| **后端** | Python 3.11 | 核心逻辑与自动化 |
| **数据库** | Notion API | 结构化存储与备份 |
| **邮件服务** | SMTP (Gmail) | 订阅者邮件推送 |
| **静态网站** | MkDocs + Material Theme | 精美的阅读体验 |
| **CI/CD** | GitHub Actions | 定时触发与自动部署 |
| **托管** | GitHub Pages | 静态网站托管 |

---

## 🚀 快速开始（Fork 并自定义）

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮

### 2. 配置 GitHub Secrets
在你的仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下 Secrets：

#### 必需配置
| Secret 名称 | 说明 | 获取方式 |
|------------|------|----------|
| `GEMINI_API_KEY` | Gemini API 密钥 | [Google AI Studio](https://aistudio.google.com/apikey) |
| `GITHUB_TOKEN` | GitHub 令牌 | 自动提供，无需额外配置 |

#### 可选配置（启用邮件推送）
| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `EMAIL_HOST` | SMTP 服务器 | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP 端口 | `587` |
| `EMAIL_USER` | 发件邮箱 | `your-email@gmail.com` |
| `EMAIL_PASSWORD` | 邮箱密码/应用专用密码 | `your-app-password` |
| `NOTION_SUBSCRIBERS_DB_ID` | Notion 订阅者数据库 ID | 从 Notion 数据库 URL 中获取 |

#### 可选配置（启用 Notion 同步）
| Secret 名称 | 说明 | 获取方式 |
|------------|------|----------|
| `NOTION_TOKEN` | Notion Integration Token | [Notion Integrations](https://www.notion.so/my-integrations) |
| `NOTION_DATABASE_ID` | Notion 数据库 ID | 从数据库 URL 中提取 |

### 3. 启用 GitHub Actions
进入 `Actions` 标签，点击 **I understand my workflows, go ahead and enable them**

### 4. 配置 GitHub Pages（可选）
1. 进入 `Settings` → `Pages`
2. Source 选择 `Deploy from a branch`
3. Branch 选择 `gh-pages` → `/root`
4. 保存后访问 `https://your-username.github.io/AI-Daily-News-Brief`

### 5. 手动触发测试
进入 `Actions` → 选择 **Daily AI Researcher & Publisher** → **Run workflow**

---

## 📂 项目结构

```
AI-Daily-News-Brief/
├── .github/
│   └── workflows/
│       └── daily_ai.yml          # GitHub Actions 工作流
├── docs/
│   ├── archives/                 # 历史简报归档
│   │   ├── 2025-12-27.md
│   │   └── index.md
│   ├── assets/                   # 网站资源
│   │   ├── logo.png
│   │   └── favicon.png
│   ├── stylesheets/
│   │   └── extra.css             # 自定义样式
│   └── index.md                  # 网站首页
├── researcher.py                 # 核心 AI 研究脚本
├── requirements.txt              # Python 依赖
├── mkdocs.yml                    # MkDocs 配置
└── README.md
```

---

## 🔧 核心功能模块

### 📝 `researcher.py` - 主程序
- `run_gemini3_research()` - 调用 Gemini 3 Pro 进行深度研究
- `save_to_notion()` - 同步到 Notion 数据库
- `send_email_newsletter()` - SMTP 邮件推送
- `publish_to_github_issue()` - 发布为 GitHub Issue
- `save_to_markdown_file()` - 生成 Markdown 文件
- `update_homepage()` - 动态更新首页

### ⚙️ 定时任务
- **执行时间**：每天早晨 **8:00 AM** (UTC+8 北京时间) 对应 **00:00 UTC**
- **触发方式**：GitHub Actions Cron 表达式
- **可手动触发**：支持 `workflow_dispatch`

---

## 📊 示例输出

每日简报包含以下内容：

- **💡 首席洞察**：对当日 AI 行业整体局势的分析
- **🔥 核心情报（4-6 条）**：
  - 来源链接 + 发布时间
  - 深度拆解（80-150 字）
  - 重要性分析
  - 社区反馈
- **🛠️ 极客推荐**：至少 2 个值得关注的开源项目
- **🔗 原始情报来源**：至少 5 个可验证的 URL

查看示例：[2025-12-27 AI 简报](https://cxyac.github.io/AI-Daily-News-Brief/archives/2025-12-27/)

---

## 🤝 贡献指南

欢迎提出建议和改进！

- **报告 Bug**：[提交 Issue](https://github.com/cxyac/AI-Daily-News-Brief/issues/new)
- **功能建议**：[提交 Feature Request](https://github.com/cxyac/AI-Daily-News-Brief/issues/new)
- **改进 Prompt**：欢迎 PR 优化 `researcher.py` 中的 Prompt

---

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=cxyac/AI-Daily-News-Brief&type=Date)](https://star-history.com/#cxyac/AI-Daily-News-Brief&Date)

---

## 📞 联系方式

- **作者**：[Clarence](https://github.com/cxyac)
- **邮箱**：通过 [GitHub Issue](https://github.com/cxyac/AI-Daily-News-Brief/issues) 联系
- **网站**：[news.helloaidev.com](https://news.helloaidev.com)

---

<div align="center">

**🎯 让 AI 为你过滤信息噪音，每天只读最重要的内容**

[立即订阅](https://tally.so/r/kd9P9J) • [查看示例](https://cxyac.github.io/AI-Daily-News-Brief/) • [Fork 项目](https://github.com/cxyac/AI-Daily-News-Brief/fork)

</div>
