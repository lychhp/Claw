import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_daily_report():
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASS')
    receiver_email = os.environ.get('EMAIL_TO')

    # 读取生成的报告
    if os.path.exists("report.txt"):
        with open("report.txt", "r", encoding="utf-8") as f:
            email_body = f.read()
    else:
        email_body = "今天没有抓取到新的 AI 资讯。"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "📅 今日 AI 大模型情报汇总"
    msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

    try:
        # 如果你用的是 Gmail，保持 smtp.gmail.com 465
        # 如果是 QQ 邮箱，请改为 smtp.qq.com
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ 每日早报已发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    send_daily_report()