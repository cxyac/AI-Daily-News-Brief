# 🚀 Deep Research 迁移实施指南

本文档提供了将 AI Daily News Brief 项目从 `generate_content` 迁移到 `Deep Research API` 的详细步骤。

---

## 📋 准备工作

### 检查清单

- [ ] 确保已有 Google AI Studio API Key
- [ ] Python 3.11+ 已安装
- [ ] Git 分支管理准备就绪
- [ ] 已阅读完整迁移计划 (`.agent/workflows/migrate-to-deep-research.md`)

---

## 第一步：验证 Deep Research 访问权限

### 1.1 运行测试脚本

```bash
# 设置 API Key (如果尚未设置)
export GEMINI_API_KEY="your-api-key-here"

# 运行测试
python test_deep_research.py
```

### 1.2 解读测试结果

#### ✅ 场景 A：Deep Research 可用
```
🎉 测试成功！您的 API Key 可以访问 Deep Research!
```
**→ 您可以直接进行迁移！跳到第二步。**

#### ⚠️ 场景 B：Deep Research 不可用
```
❌ 您的 API Key 尚未获得 Deep Research 访问权限
```
**→ 需要申请访问权限：**

1. 访问 [Google AI Studio](https://aistudio.google.com)
2. 查看您的 API 访问权限
3. 如需要，申请加入 Deep Research allowlist
4. 等待批准期间，可以继续使用现有方案

#### ✅ 场景 C：降级方案可用
```
✅ 降级方案可用！
```
**→ 即使 Deep Research 不可用，您的项目仍会正常运行。**

---

## 第二步：创建测试分支

```bash
# 确保在项目根目录
cd /Users/clarence/2026dev/AI-Daily-News-Brief

# 创建并切换到新分支
git checkout -b feature/deep-research-migration

# 查看当前分支
git branch
```

---

## 第三步：备份当前配置

```bash
# 备份原始 researcher.py
cp researcher.py researcher_original.py

# 提交备份
git add researcher_original.py
git commit -m "Backup original researcher.py before Deep Research migration"
```

---

## 第四步：本地测试 Deep Research 版本

### 4.1 直接测试新版脚本

```bash
# 运行 Deep Research 版本（不影响原有文件）
python researcher_deep_research.py
```

**预期行为：**
- 如果 Deep Research 可用：会花费 5-15 分钟完成研究
- 如果 Deep Research 不可用：自动降级到原有方案
- 生成的文件与原版相同：`docs/archives/YYYY-MM-DD.md`

### 4.2 检查生成的内容

```bash
# 查看最新生成的文件
ls -lt docs/archives/ | head -5

# 查看内容质量
cat docs/archives/$(date +%Y-%m-%d).md
```

### 4.3 质量对比

**检查项目：**
- [ ] 是否包含 4-6 条独立的新闻情报？
- [ ] 每条情报是否有来源 URL？
- [ ] 信息是否来自最近 24 小时？
- [ ] 分析深度是否优于原版？
- [ ] 格式是否符合 Notion/GitHub Issue 的要求？

**如果满意，继续下一步；如果不满意，调整 prompt 并重新测试。**

---

## 第五步：替换主脚本

### 选项 A：完全替换（推荐）

```bash
# 用新版本替换旧版本
cp researcher_deep_research.py researcher.py

# 注意：需要将 researcher_deep_research.py 中省略的辅助函数补全
# 这些函数包括：
# - split_content_to_blocks
# - save_to_notion
# - update_archive_index
# - update_homepage
# - save_to_markdown_file
# - publish_to_github_issue
# - send_email_newsletter
```

### 选项 B：渐进式迁移（更安全）

修改 `researcher.py`，仅替换核心研究函数：

```python
# 在文件顶部导入新函数
from researcher_deep_research import run_deep_research, run_gemini3_research_fallback

# 在 main 函数中使用新方法
if __name__ == "__main__":
    # ... 省略前面的代码
    
    # 使用 Deep Research（带降级）
    try:
        raw_report = run_deep_research()
    except:
        raw_report = run_gemini3_research_fallback()
    
    # ... 后续流程不变
```

---

## 第六步：更新依赖

确保 `requirements.txt` 是最新的：

```txt
google-genai>=1.0.0
notion-client
PyGithub
markdown
```

安装依赖：

```bash
pip install --upgrade -r requirements.txt
```

---

## 第七步：本地完整测试

### 7.1 设置所有环境变量

```bash
export GEMINI_API_KEY="your-key"
export NOTION_TOKEN="your-token"
export NOTION_DATABASE_ID="your-db-id"
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="your-username/AI-Daily-News-Brief"
```

### 7.2 运行完整流程

```bash
python researcher.py
```

### 7.3 验证所有输出

- [ ] Markdown 文件已生成 (`docs/archives/YYYY-MM-DD.md`)
- [ ] Notion 数据库已同步
- [ ] GitHub Issue 已创建（如果配置了）
- [ ] 邮件已发送（如果配置了测试收件人）

---

## 第八步：提交代码

```bash
# 查看修改
git status
git diff

# 添加所有更改
git add .

# 提交
git commit -m "Migrate to Deep Research API with fallback mechanism

- Add Deep Research Agent for multi-round research
- Implement automatic fallback to generate_content
- Add comprehensive error handling
- Include detailed research prompt for better results"

# 推送到远程分支
git push origin feature/deep-research-migration
```

---

## 第九步：GitHub Actions 测试

### 9.1 更新 workflow（如需要）

检查 `.github/workflows/daily_ai.yml` 是否需要调整超时时间：

```yaml
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 90  # 增加超时时间，因为 Deep Research 可能需要 20+ 分钟
    
    steps:
      # ... 其他步骤不变
      
      - name: Run Research & Generate File
        timeout-minutes: 75  # 为研究步骤单独设置超时
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          # ... 其他环境变量
        run: python researcher.py
```

### 9.2 手动触发测试

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Daily AI Researcher & Publisher**
4. 点击 **Run workflow**
5. 观察执行过程（可能需要 15-30 分钟）

### 9.3 监控执行

**正常日志应包含：**
```
🔬 正在启动 Deep Research Agent...
✅ 研究任务已启动: interactions/xxxxx
⏳ [1] 状态: running | 已耗时: 0.5 分钟
⏳ [2] 状态: running | 已耗时: 1.0 分钟
...
✅ 研究完成！耗时: 12.3 分钟
```

**如果出现降级：**
```
⚠️ Deep Research 失败，使用降级方案
🔄 使用降级方案: Gemini 3 Pro generate_content
✅ 降级方案执行成功
```

---

## 第十步：合并到主分支

### 10.1 创建 Pull Request

如果 GitHub Actions 测试成功：

1. 在 GitHub 创建 PR: `feature/deep-research-migration` → `main`
2. 填写 PR 描述（可参考下方模板）
3. Review 代码变更
4. 合并 PR

**PR 描述模板：**

```markdown
## 🚀 升级到 Deep Research API

### 主要变更
- ✅ 集成 Gemini Deep Research Agent 进行多轮深度研究
- ✅ 实现自动降级机制，确保服务稳定性
- ✅ 优化研究 Prompt，提升内容质量
- ✅ 添加完整的错误处理和状态监控

### 预期收益
- 📈 信息深度：从单次搜索提升到多轮迭代研究
- 📊 覆盖广度：自动发现更多相关信息源
- 🎯 内容质量：更深入的分析和洞察

### 测试结果
- [x] 本地测试通过
- [x] GitHub Actions 测试通过
- [x] 降级机制验证通过
- [x] 所有输出渠道正常（Markdown, Notion, GitHub Issue, Email）

### 风险控制
- 降级方案：如 Deep Research 不可用，自动使用原有方案
- 超时保护：最长研究时间 60 分钟
- 成本监控：建议关注 API 使用量
```

### 10.2 合并后监控

合并后的前 3 天，每天检查：
- [ ] GitHub Actions 是否按时触发
- [ ] 生成的内容质量如何
- [ ] 是否频繁触发降级机制
- [ ] API 费用是否在预期内

---

## 第十一步：性能优化（可选）

### 11.1 调整研究深度

如果觉得研究太慢或太浅，可以调整 prompt：

**更快速但较浅的研究：**
```python
research_task = f"""
Research Task: Quick AI news summary for {current_date}

Time limit: Complete within 5 minutes
Focus: Top 3-4 major announcements only
Sources: Prioritize official blogs and major tech news sites
...
"""
```

**更深入但较慢的研究：**
```python
research_task = f"""
Research Task: Comprehensive AI industry analysis for {current_date}

Depth: Deep dive into each topic with multi-source verification
Coverage: Find at least 6-8 significant developments
Community: Include extensive Reddit/HN sentiment analysis
...
"""
```

### 11.2 成本控制

查看 [API 定价](https://ai.google.dev/pricing):
- Deep Research 通常比标准 API 贵 2-5 倍
- 每天运行一次的预估成本：$0.10 - $0.50 USD
- 建议设置 Google Cloud 预算告警

### 11.3 缓存优化

如果多次测试，考虑添加缓存：

```python
import hashlib
import json
from pathlib import Path

def get_cached_research(date_str):
    cache_dir = Path(".cache/deep_research")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{date_str}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None

def save_cached_research(date_str, result):
    cache_dir = Path(".cache/deep_research")
    cache_file = cache_dir / f"{date_str}.json"
    cache_file.write_text(json.dumps(result, ensure_ascii=False))
```

---

## 🆘 故障排除

### 问题 1: Deep Research 一直卡在 "running"

**可能原因：**
- 任务太复杂
- API 服务繁忙

**解决方案：**
1. 等待更长时间（最多 60 分钟）
2. 简化研究任务描述
3. 手动取消并使用降级方案

### 问题 2: 返回格式不符合预期

**解决方案：**
- `reformat_with_ai()` 函数会自动处理
- 如仍有问题，手动调整 conversion_prompt

### 问题 3: API 报错 "Permission Denied"

**原因：**
- API Key 没有 Deep Research 权限

**解决方案：**
1. 申请 Deep Research 访问权限
2. 临时使用降级方案

### 问题 4: GitHub Actions 超时

**解决方案：**
```yaml
# 在 .github/workflows/daily_ai.yml 增加超时
jobs:
  build-and-deploy:
    timeout-minutes: 90
```

---

## 📊 预期成果

### 内容质量提升

**迁移前 (generate_content):**
- 单次搜索，可能遗漏重要信息
- 依赖 prompt 设计
- 较浅的分析

**迁移后 (Deep Research):**
- 多轮搜索，覆盖更全面
- AI 自主规划研究策略
- 更深入的洞察和关联分析

### 时间成本

**迁移前:** 30 秒 - 2 分钟  
**迁移后:** 5 - 20 分钟

### 财务成本

**迁移前:** ~$0.01 - $0.05 USD/天  
**迁移后:** ~$0.10 - $0.50 USD/天

---

## ✅ 最终检查清单

在宣布迁移完成前，确保：

- [ ] 本地测试通过
- [ ] GitHub Actions 定时任务正常
- [ ] 生成的 Markdown 文件格式正确
- [ ] Notion 同步无误
- [ ] GitHub Issue 正常发布
- [ ] 邮件推送正常（如已配置）
- [ ] 网站部署成功（GitHub Pages）
- [ ] 用户反馈积极
- [ ] API 成本在预算内
- [ ] 降级机制验证有效

---

## 🎉 恭喜！

您已成功将项目升级到 Deep Research Agent！

现在您的 AI Daily News Brief 将提供更深入、更全面的行业洞察。

**下一步建议：**
1. 收集用户反馈，持续优化 research prompt
2. 监控 API 成本和性能指标
3. 考虑添加更多数据源（如 Twitter API, Reddit API）
4. 探索 Deep Research 的其他高级功能

---

**需要帮助？**
- 查看详细规划: `.agent/workflows/migrate-to-deep-research.md`
- 查看测试脚本: `test_deep_research.py`
- 查看新版代码: `researcher_deep_research.py`
- 提交 GitHub Issue: [项目仓库](https://github.com/cxyac/AI-Daily-News-Brief/issues)

**祝您的项目运行顺利！🚀**
