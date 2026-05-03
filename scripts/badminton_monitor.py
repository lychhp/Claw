import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 1. 抓取逻辑
def fetch_badminton_streams():
    m3u_url = "https://iptv-org.github.io/iptv/categories/sports.m3u"
    try:
        response = requests.get(m3u_url, timeout=15)
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

# 2. 发送逻辑 (完全参照你的 main.py 图片)
def send_notification(content):
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    receiver = os.environ.get('RECEIVER_EMAIL')

    # 按照你图片里的逻辑，把标题直接写在邮件里
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header("🏸 羽毛球直播源自动提醒", 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(sender, password)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        print("邮件推送成功")
    except Exception as e:
        print(f"邮件推送失败: {e}")

# 3. 执行入口
if __name__ == "__main__":
    print("正在搜索羽毛球直播源...")
    live_content = fetch_badminton_streams()
    
    if live_content:
        send_notification(live_content)
    else:
        print("当前没有搜集到直播源。")