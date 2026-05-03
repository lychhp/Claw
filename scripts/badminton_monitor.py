import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ==========================================
# 1. 数据抓取模块 (Data Source)
# ==========================================

def fetch_badminton_streams():
    """
    从公开的 IPTV 列表和 YouTube 关键词搜索直播源
    """
    all_results = []
    
    # --- 源 A: IPTV 聚合源 ---
    m3u_url = "https://iptv-org.github.io/iptv/categories/sports.m3u"
    try:
        response = requests.get(m3u_url, timeout=15)
        if response.status_code == 200:
            lines = response.text.split('\n')
            for i in range(len(lines)):
                # 匹配关键词：Badminton 或 BWF
                if "Badminton" in lines[i] or "BWF" in lines[i]:
                    if i + 1 < len(lines) and lines[i+1].startswith("http"):
                        all_results.append(f"📺 IPTV源: {lines[i]}\n🔗 链接: {lines[i+1]}")
    except Exception as e:
        print(f"IPTV 抓取异常: {e}")

    # --- 源 B: YouTube 搜索逻辑 (模拟思路) ---
    # 这里你可以根据需要使用 YouTube API，现在先以生成搜索链接为主
    bwf_search_live = "https://www.youtube.com/results?search_query=badminton+live+now&sp=EgJAAQ%253D%253D"
    all_results.append(f"🎥 YouTube 实时搜索 (BWF/直播): \n🔗 {bwf_search_live}")

    return "\n\n---\n\n".join(all_results) if all_results else None

# ==========================================
# 2. 邮件发送模块 (Notification)
# ==========================================

def send_notification(content):
    """
    完全参照你 main.py 的发送逻辑
    """
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    receiver = os.environ.get('RECEIVER_EMAIL')

    if not all([sender, password, receiver]):
        print("错误：环境变量 GMAIL_USER, GMAIL_PASS 或 RECEIVER_EMAIL 未配置")
        return

    # 构建邮件内容
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header("🏸 羽毛球直播源自动提醒", 'utf-8')

    try:
        # 使用 Gmail SMTP 转发
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(sender, password)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        print("✅ 邮件推送成功！")
    except Exception as e:
        print(f"❌ 邮件推送失败: {e}")

# ==========================================
# 3. 自动化入口 (Main Execution)
# ==========================================

if __name__ == "__main__":
    print("🚀 正在启动羽毛球直播源扫描器...")
    
    # 调用抓取函数
    live_content = fetch_badminton_streams()
    
    if live_content:
        print("🔍 搜集到活跃资源，准备发送...")
        send_notification(live_content)
    else:
        # 如果没有抓取到特定的 m3u8，至少你可以选择是否发个提醒，或者静默结束
        print("😴 当前 IPTV 列表暂无羽毛球活跃直播，期待比赛日！")