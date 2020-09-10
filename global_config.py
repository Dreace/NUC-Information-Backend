import os

app_secret = ''

NAME = ""
PASSWD = ""
proxies = {}
proxy_status_url = ""
get_cookies_url = ""

redis = {
    'host': '',
    'password': '',
    'port': 6379
}
mysql = {
    'host': '',
    'user': '',
    'password': ''
}

qiniu = {
    'access_key': '',
    'secret_key': ''
}

rabbitmq = {
    'username': os.environ["RABBITMQ_USERNAME"],
    'password': os.environ["RABBITMQ_PASSWORD"],
    'host': os.environ["RABBITMQ_HOST"],
    'port': int(os.environ["RABBITMQ_PORT"])
}
