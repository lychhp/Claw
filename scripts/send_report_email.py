#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送日报邮件脚本
依赖：yagmail
"""
import os
import sys
from datetime import datetime

try:
    import yagmail
except ImportError:
    print("[INFO] 未检测到 yagmail，正在安装...")
    os.system(f"pip install yagmail")
    import yagmail

def send_email(subject, content, to_email, user, password, attachment=None):
    yag = yagmail.SMTP(user=user, password=password)
    yag.send(
        to=to_email,
        subject=subject,
        contents=[content],
        attachments=[attachment] if attachment else None
    )
    print(f"[OK] 邮件已发送到 {to_email}")

def main():
    # 环境变量读取
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    to_email = os.environ.get("EMAIL_TO")
    
    if not (user and password and to_email):
        print("[ERROR] 缺少邮件配置（EMAIL_USER, EMAIL_PASS, EMAIL_TO）")
        sys.exit(1)
    
    # 查找最新日报
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    files = [f for f in os.listdir(reports_dir) if f.startswith("daily_ai_report_") and f.endswith(".md")]
    if not files:
        print("[ERROR] 未找到日报文件")
        sys.exit(1)
    latest_file = sorted(files)[-1]
    report_path = os.path.join(reports_dir, latest_file)
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"AI大模型资讯日报 - {today}"
    
    send_email(subject, content, to_email, user, password, attachment=report_path)

if __name__ == "__main__":
    main()
