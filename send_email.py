import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    # 1. 安全读取 GitHub Secrets 传进来的环境变量
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASS')
    receiver_email = os.environ.get('EMAIL_TO')

    if not all([sender_email, sender_password, receiver_email]):
        print("❌ 错误：环境变量未正确加载，请检查 GitHub Secrets 配置！")
        return

    # 2. 构建邮件内容
    subject = "🎉 Claw 智能体汇报：自动化工作流测试成功！"
    body = """
    你好！
    
    当你收到这封邮件时，说明你的 GitHub Actions 工作流已经完美跑通了！
    Python 脚本成功读取了 Secrets，并完成了自动发送。
    
    接下来，你可以把真实的网络抓取数据填入这里了。
    
    你的专属 AI 助手
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 3. 发送邮件 (这里以 Gmail 为例，SMTP 服务器为 smtp.gmail.com，端口 465)
    # 如果你是 QQ 邮箱，请将 smtp.gmail.com 改为 smtp.qq.com
    try:
        print("正在连接 SMTP 服务器...")
        # 使用 SSL 加密连接
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ 邮件发送成功！请查收收件箱。")
    except Exception as e:
        print(f"❌ 邮件发送失败，错误详情: {e}")

if __name__ == "__main__":
    send_test_email()