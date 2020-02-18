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
            code = -3
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
                    "Course_Name": item["kcmc"] if "kcmc" in item else "",
                    "Course_Credit": float(item["xf"]) if "xf" in item else "",
                    "Course_Grade": item["bfzcj"],
                    "Course_Grade_Point": float(item["jd"]) if "jd" in item else ""
                })
            data = list(grades.values())
            g_a, g_b = 0, 0
            for item_i in data:
                a, b = 0, 0
                for item_j in item_i:
                    if item_j["Course_Credit"] and item_j["Course_Grade_Point"]:
                        t = item_j["Course_Credit"] * item_j["Course_Grade_Point"]
                        a += t
                        g_a += t
                        b += item_j["Course_Credit"]
                        g_b += item_j["Course_Credit"]
                if b:
                    item_i.append({
                        "Course_Name": "学期平均绩点",
                        "Course_Grade_Point": round(a / b, 2)
                    })
            if g_b:
                data[-1].append({
                    "Course_Name": "总平均绩点",
                    "Course_Grade_Point": round(g_a / g_b, 2)
                })
    return {"message": message, "code": code, "data": data}
