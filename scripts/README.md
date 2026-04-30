# AI 大模型资讯日报系统

> 自动化每日采集开源 AI 大模型资讯，生成 Markdown 日报。

## 📋 功能概览

- ✅ **自动化采集** - 每天早上 8 点 UTC 自动运行
- ✅ **多源资讯** - GitHub Trending、HuggingFace、ArXiv
- ✅ **Markdown 日报** - 自动格式化生成，按源分类
- ✅ **自动提交** - 日报直接提交到仓库

## 🏗 项目结构

```
.
├── scripts/
│   ├── fetch_ai_models_news.py   # 主爬虫脚本
│   ├── requirements.txt            # Python 依赖
│   └── test_local.sh               # 本地测试脚本
├── .github/workflows/
│   └── daily-ai-news.yml           # GitHub Actions 工作流
└── reports/
    └── daily_ai_report_YYYY-MM-DD.md  # 生成的日报
```

## 🚀 快速开始

### 本地测试

```bash
# 方式 1: 运行测试脚本
bash scripts/test_local.sh

# 方式 2: 手动执行
pip install -r scripts/requirements.txt
python scripts/fetch_ai_models_news.py
```

### 自动化运行

GitHub Actions 工作流已启用，会在以下情况下执行：

1. **定时任务** - 每天早上 8:00 UTC
2. **手动触发** - 在 GitHub Actions 页面点击 "Run workflow"

## ⚙️ 配置说明

### 修改运行时间

编辑 `.github/workflows/daily-ai-news.yml`，修改 cron 表达式：

```yaml
schedule:
  - cron: '0 8 * * *'  # 早上 8 点 UTC
```

时区转换参考：
- UTC 8:00 = 北京时间 16:00（下午 4 点）
- UTC 0:00 = 北京时间 08:00（早上 8 点）

**常用 Cron 表达式**：
- `0 0 * * *` - 每天 00:00 UTC
- `0 8 * * *` - 每天 08:00 UTC
- `0 16 * * *` - 每天 16:00 UTC
- `0 */6 * * *` - 每 6 小时

### 添加新数据源

在 `fetch_ai_models_news.py` 中：

1. 创建新的采集器类，继承 `NewsCollector`
2. 实现 `fetch()` 方法
3. 在 `main()` 函数中添加到 `collectors` 列表

示例：

```python
class CustomCollector(NewsCollector):
    def fetch(self) -> List[Dict[str, str]]:
        # 实现你的采集逻辑
        return [
            {
                "title": "Example Title",
                "url": "https://example.com",
                "description": "Example description",
                "source": "Custom Source"
            }
        ]

# 在 main() 中添加
collectors = [
    GitHubTrendingCollector(),
    HuggingFaceCollector(),
    ArxivCollector(),
    CustomCollector(),  # 新增
]
```

## 📊 输出示例

生成的日报格式如下：

```markdown
# 🤖 AI 大模型资讯日报

**生成时间**: 2026-04-29 12:34:56

> 每日自动收集最新的开源 AI 大模型资讯...

## 📰 GitHub Trending
1. **[项目名称](https://github.com/...)**
   - 项目描述...

## 📰 HuggingFace
1. **[模型名称](https://huggingface.co/...)**
   - 模型描述...

...
```

## 🔧 故障排查

### 工作流没有自动运行？

1. 检查 `.github/workflows/daily-ai-news.yml` 文件是否存在且有效
2. 确保仓库已启用 GitHub Actions
3. 在 Actions 标签页查看执行历史和错误信息

### 采集失败或结果为空？

1. 检查网络连接
2. 查看 Action 日志中的错误信息
3. 确认各数据源是否仍可访问：
   - GitHub: https://github.com/trending
   - HuggingFace: https://huggingface.co/api/models
   - ArXiv: http://arxiv.org/rss/cs.AI/recent

### 如何调试？

在本地运行测试脚本：

```bash
bash scripts/test_local.sh
```

查看 `reports/` 目录下的生成日报。

## 📝 日志和工件

- **日志** - 在 GitHub Actions 页面查看每次运行的详细日志
- **工件** - 每次运行生成的日报会保存为工件，可下载，保留 30 天

## 🎯 future enhancement

- [ ] 添加邮件通知功能
- [ ] 集成数据库存储历史资讯
- [ ] 添加资讯搜索和过滤功能
- [ ] 支持自定义分类和标签
- [ ] 生成 HTML 版本的日报

## 📄 许可证

此项目采用 MIT 许可证。

---

**最后更新**: 2026-04-29
**维护者**: Claw AI Agent
