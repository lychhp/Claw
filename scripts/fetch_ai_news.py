import feedparser
import os

def fetch_news():
    # 定义订阅源 (RSS)
    feeds = {
        "Hugging Face 博客": "https://huggingface.co/blog/feed.xml",
        "Arxiv AI 论文": "http://export.arxiv.org/rss/cs.AI",
    }
    
    report_content = "🤖 Claw 智能体：今日 AI 大模型资讯早报\n"
    report_content += "="*40 + "\n\n"

    for source, url in feeds.items():
        print(f"正在抓取: {source}...")
        feed = feedparser.parse(url)
        report_content += f"【{source}】\n"
        
        # 每个源只取前 5 条最新的
        for entry in feed.entries[:5]:
            report_content += f"- {entry.title}\n  链接: {entry.link}\n\n"
        
    # 将抓取的内容保存到本地文件
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("✅ 报告生成成功：report.txt")

if __name__ == "__main__":
    fetch_news()