import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(stock_list, to_email, from_email, password):
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = 'Agentic AI Stock Alert'

    body = ""
    for s in stock_list:
        body += f"{s['symbol']}: Price={s['price']}, ROE={s['roe']}, PEG={s['peg_ratio']}\nRecommendation: {s.get('explanation','N/A')}\n\n"

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
