from flask import Response
from flask import request

from plugins_v2._login_v2.login_v2 import login
from . import api
from .config import *


@api.route('/GetCourseTable', methods=['GET'])
def handle_get_course_table():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_course_table(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_course_table(name, passwd):
    message = "OK"
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, str):
            code = -3
            message = session
        else:
            post_data = {
                "xnm": 2019,
                "xqm": 12
            }
            course_table = session.post(course_table_url, data=post_data).json()
            tables = []
            cnt = 0
            name_dict = {}
            for index, table in enumerate(course_table["kbList"]):
                spited = table["jcor"].split("-")
                if table["kcmc"] not in name_dict:
                    name_dict[table["kcmc"]] = cnt
                    cnt += 1
                tables.append({
                    "Course_Number": table["kch_id"],
                    "Course_Name": table["kcmc"],
                    "Course_Credit": table["xf"],
                    "Course_Test_Type": table["khfsmc"],
                    "Course_Teacher": table["xm"],
                    "Course_Week": table["zcd"],
                    "Course_Color": name_dict[table["kcmc"]],
                    "Course_Time": table["xqj"],
                    "Course_Start": spited[0],
                    "Course_Length": int(spited[1]) - int(spited[0]) + 1,
                    "Course_Building": table["xqmc"],
                    "Course_Classroom": table["cdmc"]
                })
            for d in course_table["sjkList"]:
                tables.append({
                    "Course_Name": d["sjkcgs"]
                })
            data = tables
    return {"message": message, "code": code, "data": data}
