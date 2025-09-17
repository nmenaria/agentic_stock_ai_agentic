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
        # Ensure any special characters are handled
        symbol = str(s['symbol'])
        price = str(s['price'])
        roe = str(s['roe'])
        peg = str(s['peg_ratio'])
        explanation = s.get('explanation', 'N/A')
        body += f"{symbol}: Price={price}, ROE={roe}, PEG={peg}\nRecommendation: {explanation}\n\n"

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
