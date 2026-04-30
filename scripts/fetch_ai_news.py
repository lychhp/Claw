import feedparser
import os
import requests
import json

def fetch_and_summarize():
    # 1. 定义资讯源
    feeds = {
        "Hugging Face": "https://huggingface.co/blog/feed.xml",
        "Arxiv AI": "http://export.arxiv.org/rss/cs.AI",
    }
    
    raw_text = ""
    for source, url in feeds.items():
        print(f"正在抓取: {source}...")
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: 
            # 安全获取摘要：先找 summary，找不到找 description，再找不到就默认'无摘要'
            summary_text = entry.get('summary', entry.get('description', '无摘要'))
            raw_text += f"标题: {entry.title}\n摘要: {summary_text[:200]}...\n链接: {entry.link}\n\n"

    # 2. 调用 DeepSeek 进行智能总结
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    # 如果你使用的是标准 API 接口，地址通常如下；如果是 Vertex AI 部署，请更换为你的 Endpoint
    api_url = "https://api.deepseek.com/v1/chat/completions" 
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""
    你是一个专业的AI技术分析师。请将以下抓取到的AI资讯总结成一份『今日情报精华』。
    要求：
    1. 风格干货、犀利，避免废话。
    2. 分点叙述，每一点后面附上原文链接。
    3. 最后给出一个“今日最值得关注”的点评。
    
    资讯内容如下：
    {raw_text}
    """

    payload = {
        "model": "deepseek-v4-flash", # 这里可以根据你的权限改为具体的模型 ID
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    print("正在连接 DeepSeek 进行智能总结...")
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        summary = response.json()['choices'][0]['message']['content']
        print("✅ 智能总结生成成功！")
    except Exception as e:
        print(f"❌ 总结失败，将发送原文。错误: {e}")
        summary = "AI总结失败，以下为原始资讯：\n\n" + raw_text

    # 3. 保存最终报告
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(summary)

if __name__ == "__main__":
    fetch_and_summarize()