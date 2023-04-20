import smtplib
from email.mime.text import MIMEText
import re


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True

    else:
        return False


def send_email(email, message):
    sender = "steamscroller@yandex.ru"
    password = "nxesvojaqoaaebrj"

    server = smtplib.SMTP("smtp.yandex.ru", 587)
    server.starttls()

    if check(email):
        try:
            server.login(sender, password)
            msg = MIMEText(message)
            msg['From'] = sender
            msg['To'] = email
            msg["Subject"] = "Steamscroller"
            server.sendmail(sender, msg['To'], msg.as_string())

            return "The message was sent successfully!"
        except Exception as error:
            return f"{error}\nCheck your login or password please!"
    else:
        return "Invalid Email"


def main():
    email = input("Your mail: ")
    message = input("Type your message: ")
    print(send_email(email=email, message=message))


if __name__ == "__main__":
    main()
