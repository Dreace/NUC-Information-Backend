import re

import bs4
import requests
from flask import request

from global_config import proxies
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.decorators.stopped import stopped
from utils.exceptions import custom_abort
from . import api
from .config import physical_login_url, physical_index_url


@api.route('/physical/login', methods=['GET'])
@check_sign(check_args={'name', 'passwd'})
@stopped()
@request_limit()
@need_proxy()
def handle_physical_login():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    login(name, passwd)
    return {
        'code': 0,
        'message': 'OK'
    }


@api.route('/physical/grade', methods=['GET'])
@check_sign({'name', 'passwd'})
@stopped()
@request_limit()
@need_proxy()
@cache({'name'})
def handle_physical_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    session = login(name, passwd)
    r = session.get(physical_index_url)
    html = r.content.decode("gbk")
    soup = bs4.BeautifulSoup(html, "html.parser")
    tds = soup.find_all(class_="forumRow")
    length = len(tds)
    i = 0
    c = 0
    g = 0
    rgx = re.compile(u'[（(](.*)[）)]')
    grade_items = []
    while i < length:
        grade = {
            "name": rgx.sub('', tds[i + 1].string),
            "grade": tds[i + 7].string
        }
        grade_items.append(grade)
        if tds[i + 7].string.isdigit():
            c += 1
        g += int(tds[i + 7].string)
        i += 8
        if g != 0:
            grade_items.append({
                "name": "平均分",
                "grade": round(g / c, 2)
            })
    return {
        'code': 0,
        'data': grade_items
    }


def login(name: str, passwd: str) -> requests.Session:
    if not name or not passwd:
        custom_abort(-3, '账号密码不能为空')
    if name.strip() != name:
        custom_abort(-3, '用户名包含空字符')
    session = requests.session()
    session.proxies = proxies
    html = session.get(physical_index_url).content
    reg = re.search('name=\"__VIEWSTATE\" value=\"(.{0,})\"', html)
    __VIEWSTATE = reg.group(1)
    post_data = {
        '__VIEWSTATE': __VIEWSTATE,
        'login1:StuLoginID': name,
        'login1:StuPassword': passwd,
        'login1:UserRole': 'Student',
        'login1:btnLogin.x': '12',
        'login1:btnLogin.y': '6',
    }
    r = session.post(physical_login_url, data=post_data)
    if r.content.decode("gbk").find(u"用户或密码错误") != -1:
        custom_abort(-3, '账号或密码错误')
    return session
