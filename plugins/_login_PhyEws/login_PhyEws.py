import re

import requests
from .config import proxies, PhyEws_post_url, PhyEws_url


def login_PhyEws(name, passwd):
    session = requests.session()
    session.proxies = proxies
    html = session.get(PhyEws_url).content
    reg = re.search("name=\"__VIEWSTATE\" value=\"(.{0,})\"", html)
    __VIEWSTATE = reg.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "login1:StuLoginID": name,
        "login1:StuPassword": passwd,
        "login1:UserRole": "Student",
        "login1:btnLogin.x": "12",
        "login1:btnLogin.y": "6",
    }
    r = session.post(PhyEws_post_url, data=data)
    if r.content.decode("gbk").find(u"用户或密码错误") != -1:
        return 2
    return session
