import json

import bs4

NAME = ""
PASSWD = ""
proxies = {}
proxy_status_url = "http://127.0.0.1:10001/status"
get_cookies_url = "http://127.0.0.1:10001/getCookies"
vpn_cookies = ""

redis_host = ""
redis_password = ""
redis_port = 6379

mysql_host = ""
mysql_user = ""
mysql_password = ""

qiniu_access_key = ''
qiniu_secret_key = ''

guest_data = {}
with open("guest_data.json", encoding="utf-8") as file:
    guest_data = json.loads(file.read())

no_limit_url = {"GetNews"}
dont_cache_url = {"Token", "ToiCal", "GetNews"}
stopped_list = {"LoginPhyEws", "GetIdleClassroom"}
need_proxy_url = {"SearchLibrary", "v2/GetCourseTable", "v2/ExportGrade", "v2/GetGrade", "v2/Login",
                  "PhysicalFitnessTestGetScoreList", "PhysicalFitnessTestGetScore", "PhysicalFitnessTestLogin",
                  "GetBookAvailableDetail", "GetClassCourseTable", "SearchLibraryByISBN", "SearchLibrary", "GetCourse",
                  "ToiCal"}

appSecret = ''

course_table_url = "http://202.207.177.39:8089/lnkbcxAction.do"


def get_term_code(session):
    html = session.post(course_table_url, data={"zxjxjhh": "1234567"}).content.decode("gbk")
    soups = bs4.BeautifulSoup(html, "lxml")
    ops = soups.find_all("option")
    terms = []
    for op in ops:
        terms.append({"value": op.attrs["value"], "name": op.text})
    return terms
