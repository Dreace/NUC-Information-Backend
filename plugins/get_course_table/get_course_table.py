import re

from flask import request
from flask import Response
import json
from . import api
from .config import *
from plugins._login.login import login


@api.route('/GetCourseTable', methods=['GET'])
def handle_get_course_table():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_course_table(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_course_table(name, passwd):
    message = "OK"
    error = ""
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
        error = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, int):
            code = -1
            error = "账号或密码错误"
            if session == 2:
                message = "账号或密码错误"
            else:
                message = "服务器异常"
        else:
            for term_code in get_term_code(session):
                _html = session.post(course_table_url, data={"zxjxjhh": term_code["value"]}).content.decode("gbk")
                t = handle_course_table_html(_html)
                data.append({"name": term_code["name"], "table": t})
    return {"message": message, "error": error, "code": code, "data": data}


def handle_course_table_html(html):
    # html = html.replace("\n", "").replace("\r", "").replace("\t", "")
    soups = bs4.BeautifulSoup(html, "lxml")
    tables = soups.select("table.titleTop2")
    t = tables[1]
    terms = []
    cnt = -1
    for tr in t.select("table.displayTag > tbody > tr"):
        tds = tr.find_all("td")
        if len(tds[0].attrs) <= 0:
            table_ = terms[-1]
            table = {u"Course_Number": table_["Course_Number"],
                     "Course_Name": table_["Course_Name"],
                     "Course_Credit": table_["Course_Credit"],
                     "Course_Attribute": table_["Course_Attribute"],
                     "Course_Test_Type": table_["Course_Test_Type"],
                     "Course_Teacher": table_["Course_Teacher"],
                     "Course_Week": table_["Course_Week"],
                     "Course_Color": cnt,
                     "Course_Time": td_tostring(tds[1].contents),
                     "Course_Start": td_tostring(tds[2].contents),
                     "Course_Length": td_tostring(tds[3].contents),
                     "Course_Building": td_tostring(tds[5].contents),
                     "Course_Classroom": td_tostring(tds[6].contents)}
        else:
            cnt += 1
            table = {"Course_Number": td_tostring(tds[1].contents),
                     "Course_Name": td_tostring(tds[2].contents),
                     "Course_Credit": td_tostring(tds[4].contents),
                     "Course_Attribute": td_tostring(tds[5].contents),
                     "Course_Test_Type": td_tostring(tds[6].contents),
                     "Course_Teacher": td_tostring(tds[7].contents).replace("*", ""),
                     "Course_Week": td_tostring(tds[10].contents),
                     "Course_Color": cnt,
                     "Course_Time": td_tostring(tds[11].contents),
                     "Course_Start": td_tostring(tds[12].contents),
                     "Course_Length": td_tostring(tds[13].contents),
                     "Course_Building": td_tostring(tds[15].contents),
                     "Course_Classroom": td_tostring(tds[16].contents)}
        terms.append(table)

    return terms


def td_tostring(data):
    if not data:
        return ""
    else:
        return re.sub(r"[\r\n\t]","",data[0])
        # return data[0].replace(" ", "")
