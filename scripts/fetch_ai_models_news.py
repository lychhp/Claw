#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 大模型资讯日报爬虫
自动从多个源抓取最新的开源 AI 大模型资讯，生成 Markdown 日报
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser

# ==================== 配置 ====================
GITHUB_TRENDING_URL = "https://github.com/trending"
HUGGINGFACE_NEW_MODELS = "https://huggingface.co/models"
ARXIV_AI_FEED = "http://arxiv.org/rss/cs.AI/recent"
GITHUB_API_BASE = "https://api.github.com"

# 爬虫超时时间
REQUEST_TIMEOUT = 10

# ==================== 数据源采集器 ====================

class NewsCollector:
    """资讯采集器基类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch(self) -> List[Dict[str, str]]:
        """获取资讯，返回列表，每个元素包含 title, url, description, source"""
        raise NotImplementedError


class GitHubTrendingCollector(NewsCollector):
    """从 GitHub Trending 采集热门 AI 项目"""
    
    def fetch(self) -> List[Dict[str, str]]:
        """采集 GitHub Trending 上的 Python 和 Machine Learning 项目"""
        items = []
        try:
            # 采集 Python 分类下的热门项目
            params = {"spoken_language_code": "", "l": "python"}
            response = requests.get(
                f"{GITHUB_TRENDING_URL}",
                params=params,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                # 简单解析 HTML，提取项目链接
                from html.parser import HTMLParser
                
                class GithubProjectParser(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.projects = []
                        self.in_article = False
                        self.current_title = None
                        self.current_url = None
                        self.current_desc = None
                        
                    def handle_starttag(self, tag, attrs):
                        attrs_dict = dict(attrs)
                        if tag == "article" and attrs_dict.get("class") and "Box-row" in attrs_dict.get("class", ""):
                            self.in_article = True
                        elif self.in_article and tag == "h2":
                            pass
                        elif self.in_article and tag == "a":
                            href = attrs_dict.get("href", "")
                            if href.startswith("/") and href.count("/") == 2:
                                self.current_url = f"https://github.com{href}"
                                self.current_title = href.strip("/")
                    
                    def handle_data(self, data):
                        if self.in_article and not self.current_desc:
                            text = data.strip()
                            if text and len(text) > 10:
                                self.current_desc = text[:150]
                    
                    def handle_endtag(self, tag):
                        if tag == "article" and self.in_article:
                            if self.current_url:
                                self.projects.append({
                                    "title": self.current_title or "Unknown",
                                    "url": self.current_url,
                                    "description": self.current_desc or "No description",
                                    "source": "GitHub Trending"
                                })
                            self.in_article = False
                            self.current_title = None
                            self.current_url = None
                            self.current_desc = None
                
                parser = GithubProjectParser()
                parser.feed(response.text)
                items = parser.projects[:5]  # 只取前 5 个
                
        except Exception as e:
            print(f"[WARNING] GitHub Trending 采集失败: {e}")
        
        return items


class HuggingFaceCollector(NewsCollector):
    """从 HuggingFace 采集新发布的大模型"""
    
    def fetch(self) -> List[Dict[str, str]]:
        """采集 HuggingFace 最新模型"""
        items = []
        try:
            # 使用 HuggingFace 的 API
            api_url = "https://huggingface.co/api/models"
            params = {
                "sort": "downloads",
                "direction": -1,
                "limit": 5
            }
            
            response = requests.get(
                api_url,
                params=params,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                models = response.json()
                
                for model in models[:5]:
                    items.append({
                        "title": model.get("id", "Unknown Model"),
                        "url": f"https://huggingface.co/{model.get('id', '')}",
                        "description": model.get("description", "No description")[:150],
                        "source": "HuggingFace"
                    })
        
        except Exception as e:
            print(f"[WARNING] HuggingFace 采集失败: {e}")
        
        return items


class ArxivCollector(NewsCollector):
    """从 ArXiv 采集 AI 论文"""
    
    def fetch(self) -> List[Dict[str, str]]:
        """采集 ArXiv 最新 AI 论文"""
        items = []
        try:
            # 使用 ArXiv RSS 源
            feed = feedparser.parse(ARXIV_AI_FEED)
            
            for entry in feed.entries[:5]:
                items.append({
                    "title": entry.get("title", "Unknown"),
                    "url": entry.get("link", ""),
                    "description": entry.get("summary", "No summary")[:150],
                    "source": "ArXiv"
                })
        
        except Exception as e:
            print(f"[WARNING] ArXiv 采集失败: {e}")
        
        return items


# ==================== Markdown 日报生成器 ====================

class NewsReportGenerator:
    """生成 Markdown 格式的日报"""
    
    def __init__(self, news_items: List[Dict[str, str]]):
        self.news_items = news_items
    
    def generate(self) -> str:
        """生成完整的 Markdown 日报"""
        now = datetime.now()
        report_date = now.strftime("%Y-%m-%d")
        report_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 按数据源分组
        grouped_news = self._group_by_source()
        
        # 生成 Markdown
        markdown = f"""# 🤖 AI 大模型资讯日报

**生成时间**: {report_time}

> 每日自动收集最新的开源 AI 大模型资讯，包含 GitHub Trending、HuggingFace 和 ArXiv 的最新动态。

---

"""
        
        for source, items in grouped_news.items():
            markdown += f"## 📰 {source}\n\n"
            
            for i, item in enumerate(items, 1):
                title = item.get("title", "Unknown")
                url = item.get("url", "#")
                description = item.get("description", "No description")
                
                markdown += f"{i}. **[{title}]({url})**\n"
                markdown += f"   - {description}\n\n"
            
            markdown += "\n"
        
        # 添加页脚
        markdown += f"""---

**报告统计**:
- 总资讯数: {len(self.news_items)}
- 数据源: {len(grouped_news)} 个

*此报告由 Claw AI 智能体自动生成*
"""
        
        return markdown
    
    def _group_by_source(self) -> Dict[str, List[Dict[str, str]]]:
        """按数据源分组资讯"""
        grouped = {}
        
        for item in self.news_items:
            source = item.get("source", "Unknown")
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(item)
        
        return grouped


# ==================== 主程序 ====================

def main():
    """主函数：采集 -> 生成 -> 保存"""
    
    print("[INFO] 开始采集 AI 大模型资讯...")
    
    # 创建采集器
    collectors = [
        GitHubTrendingCollector(),
        HuggingFaceCollector(),
        ArxivCollector(),
    ]
    
    all_news = []
    
    # 执行采集
    for collector in collectors:
        collector_name = collector.__class__.__name__
        print(f"[INFO] 执行 {collector_name}...")
        try:
            news = collector.fetch()
            all_news.extend(news)
            print(f"[OK] {collector_name} 采集到 {len(news)} 条资讯")
        except Exception as e:
            print(f"[ERROR] {collector_name} 失败: {e}")
    
    if not all_news:
        print("[ERROR] 未采集到任何资讯，退出")
        return 1
    
    print(f"[INFO] 总共采集到 {len(all_news)} 条资讯")
    
    # 生成日报
    print("[INFO] 生成 Markdown 日报...")
    generator = NewsReportGenerator(all_news)
    report_content = generator.generate()
    
    # 确定输出路径
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 按日期命名
    report_date = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(reports_dir, f"daily_ai_report_{report_date}.md")
    
    # 保存日报
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"[OK] 日报已保存到: {output_file}")
    except Exception as e:
        print(f"[ERROR] 保存日报失败: {e}")
        return 1
    
    # 输出日报内容用于 GitHub Actions 日志
    print("\n" + "="*60)
    print("日报内容预览:")
    print("="*60)
    print(report_content[:500] + "...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
