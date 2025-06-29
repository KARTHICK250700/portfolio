import smtplib, ssl
from email.mime.text import MIMEText

YOUR_EMAIL = 'kingking250700@gmail.com'
EMAIL_PASSWORD = 'kdvp hgcs ukis pqzw'

def send_email_otp(to_email, otp):
    try:
        msg = MIMEText(f"Your OTP is: {otp}")
        msg['Subject'] = "Your Login OTP"
        msg['From'] = YOUR_EMAIL
        msg['To'] = to_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(YOUR_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email sending failed:", e)
        return False
