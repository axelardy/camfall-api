import smtplib


def send_notification(camera,target,username):
    host = "smtp.gmail.com"
    port = 587
    from_mail = "axelardy06@gmail.com"
    to_mail = target
    password = "lcrxdwcjbzrkjyjq"
    msg = f"""Subject: Notification from Server
Hi {username}!
Fall detected from camera {camera}! Please check the server for more details.
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

