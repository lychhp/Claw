import requests
import re

def fetch_badminton_streams():
    # 这是一个高质量的全球公开 IPTV 源地址
    m3u_url = "https://iptv-org.github.io/iptv/categories/sports.m3u"
    try:
        response = requests.get(m3u_url, timeout=15)
        lines = response.text.split('\n')
        
        matches = []
        for i in range(len(lines)):
            # 搜索关键词：Badminton, BWF, 或特定的体育频道名
            if "Badminton" in lines[i] or "BWF" in lines[i]:
                # 如果当前行是频道信息，下一行通常就是播放链接
                if i + 1 < len(lines) and lines[i+1].startswith("http"):
                    matches.append(f"{lines[i]}\nLink: {lines[i+1]}")
        
        return "\n\n".join(matches) if matches else "今日暂无活跃羽毛球直播源。"
    except Exception as e:
        return f"抓取失败: {str(e)}"

if __name__ == "__main__":
    content = fetch_badminton_streams()
    print(content) # 给 GitHub Action 读取输出