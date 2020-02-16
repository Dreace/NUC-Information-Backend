import json
import re

import bs4
from flask import Response
from flask import request

from plugins._login_PhyEws.login_PhyEws import login_PhyEws
from . import api
from .config import PhyEws_grade_url


@api.route('/GetPhyEwsGrade', methods=['GET'])
def handle_get_PhyEws_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_PhyEws_grade(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_PhyEws_grade(name, passwd):
    message = "OK"
    error = ""
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "登陆失败"
        error = "账号密码不能为空"
    else:
        session = login_PhyEws(name, passwd)
        r = session.get(PhyEws_grade_url)
        html = r.content.decode("gbk")
        soup = bs4.BeautifulSoup(html, "html.parser")
        tds = soup.find_all(class_="forumRow")
        length = len(tds)
        i = 0
        c = 0
        g = 0
        rgx = re.compile(u'[（(](.*)[）)]')
        while i < length:
            grade = {"Course_Name": rgx.sub('', tds[i + 1].string),
                     u"Course_Grade": tds[i + 7].string}
            data.append(grade)
            if tds[i + 7].string.isdigit():
                c += 1
            g += int(tds[i + 7].string)
            i += 8
            if g != 0:
                data.append({"Course_Name": "平均分",
                             u"Course_Grade": round(1.0 * g / c, 2)})
    return {"message": message, "error": error, "code": code, "data": data}
