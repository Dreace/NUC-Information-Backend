from flask import Response
from flask import request

from plugins_v2._login_v2.login_v2 import login
from . import api
from .config import *


@api.route('/GetGrade', methods=['GET'])
def handle_get_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_grade(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_grade(name, passwd):
    message = "OK"
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, str):
            code = -1
            message = session
        else:
            post_data = {
                "queryModel.showCount": 1000,
            }
            grade = session.post(grade_url, post_data).json()
            grades = {}
            for item in grade["items"]:
                dict_key = item["xnmmc"] + "-" + item["xqmmc"]
                if dict_key not in grades:
                    grades[dict_key] = []
                grades[dict_key].append({
                    "Course_Name": item["kcmc"],
                    "Course_Credit": item["xf"] if "xf" in item else "",
                    "Course_Grade": item["bfzcj"],
                    "Course_Grade_Point": item["jd"] if "jd" in item else ""
                })
            data = list(grades.values())
    return {"message": message, "code": code, "data": data}
