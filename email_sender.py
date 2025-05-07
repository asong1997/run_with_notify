import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, from_email, password, to_email):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        print("📬 邮件发送成功")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
    finally:
        server.quit()