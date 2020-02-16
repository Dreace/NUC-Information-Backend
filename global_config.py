import json

import bs4

proxies = {}
vpn_cookies = ""
course_table_url = "http://202.207.177.39:8089/lnkbcxAction.do"

redis_host = ""
redis_port = 6379
redis_password = ""

mysql_host = ""
mysql_user = ""
mysql_password = ""

qiniu_access_key = ''
qiniu_secret_key = ''
no_limit_url = {"GetNews"}

guest_data = {}
with open("guest_data.json", encoding="utf-8") as file:
    guest_data = json.loads(file.read())

request_limit = 0
request_limit_max = 20

dont_cache_url = {"Token", "ToiCal", "GetNews"}

appSecret = ''


def get_term_code(session):
    html = session.post(course_table_url, data={"zxjxjhh": "1234567"}).content.decode("gbk")
    soups = bs4.BeautifulSoup(html, "lxml")
    ops = soups.find_all("option")
    terms = []
    for op in ops:
        terms.append({"value": op.attrs["value"], "name": op.text})
    return terms
