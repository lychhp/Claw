import os
import sys
import requests

# 将根目录加入路径，方便导入 send_email.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from send_email import send_notification # 假设你的 send_email.py 里有这个函数

def fetch_badminton_streams():
    m3u_url = "https://iptv-org.github.io/iptv/categories/sports.m3u"
    try:
        response = requests.get(m3u_url, timeout=15)
        # 增加判断，确保 response 有内容
        if not response.text:
            return None
            
        lines = response.text.split('\n')
        matches = []
        for i in range(len(lines)):
            if "Badminton" in lines[i] or "BWF" in lines[i]:
                if i + 1 < len(lines) and lines[i+1].startswith("http"):
                    matches.append(f"{lines[i]}\nLink: {lines[i+1]}")
        
        return "\n\n".join(matches) if matches else None
    except Exception as e:
        print(f"抓取异常: {e}")
        return None

if __name__ == "__main__":
    content = fetch_badminton_streams()
    
    if content:
        print("发现直播源，准备发送邮件...")
        # 直接调用你现有的发送逻辑
        # 注意：这里需要匹配你 send_email.py 里的函数名和参数
        # 假设你的函数签名是 send_notification(subject, body)
        send_notification("🏸 羽毛球直播源更新", content)
    else:
        print("今日暂无直播源，跳过发送。")