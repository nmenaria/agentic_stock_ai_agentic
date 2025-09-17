import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_email(stock_list, to_email=config.TO_EMAIL, from_email=config.FROM_EMAIL, password=config.EMAIL_PASSWORD):
    if not (from_email and password and to_email):
        print("Dummy email mode: skipping email send.")
        return False

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = 'Agentic AI Stock Alert'

    body = ""
    for s in stock_list:
        body += f"{s['symbol']}: Price={s['price']}, ROE={s['roe']}, PEG={s['peg_ratio']}\nRecommendation: {s.get('explanation','N/A')}\n\n"

    message.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
