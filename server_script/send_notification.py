import smtplib


def send_notification(camera):
    host = "smtp.gmail.com"
    port = 587
    from_mail = "axelardy06@gmail.com"
    to_mail = 'axelardywt@gmail.com'
    password = "lcrxdwcjbzrkjyjq"
    msg = """Subject: Notification from Server
Fall detected from {camera}! Please check the server for more details.
Thanks"""

    smtp = smtplib.SMTP(host, port)

    status_code, response = smtp.ehlo()
    print(f"[*] Echoing the server: {status_code} {response}")
    status_code, response = smtp.starttls()
    print(f"[*] Starting TLS connection : {status_code} {response}")
    status_code, response = smtp.login(from_mail, password)
    print(f"[*] Logging in : {status_code} {response}")
    smtp.sendmail(from_mail, to_mail, msg)
    print("Mail Sent Successfully!")
    smtp.quit()

