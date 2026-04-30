import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
EMAIL_TO = os.environ.get('EMAIL_TO')

if not all([EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
    raise ValueError('EMAIL_USER, EMAIL_PASS, EMAIL_TO 环境变量必须全部设置')

msg = MIMEText('这是一封测试邮件，来自 GitHub Actions 自动化脚本。', 'plain', 'utf-8')
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_TO
msg['Subject'] = Header('测试邮件 - GitHub Actions', 'utf-8')

try:
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:  # 这里以QQ邮箱为例，如用其他邮箱请修改
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())
    print('邮件发送成功')
except Exception as e:
    print('邮件发送失败:', e)
