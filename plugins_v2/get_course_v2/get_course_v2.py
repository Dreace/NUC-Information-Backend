import json

import pymysql
from flask import Response
from flask import request

from utils.sql_helper import SQLHelper
from . import api


@api.route('/GetCourse', methods=['GET'])
def handle_get_course():
    keywords = request.args.get('keywords', "")
    res = get_course(keywords)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_course(keywords):
    message = "OK"
    error = ""
    code = 0
    data = []
    keywords = pymysql.escape_string(keywords)
    keywords_map = "".join(map(lambda k: "(?=.*%s)" % k, keywords.split(" ")))
    sql = "SELECT * FROM `课程-2020-1` WHERE CONCAT_WS('', `学院`, `课程名`, `教师`) REGEXP '%s^.*$'" % keywords_map
    for index, row in enumerate(SQLHelper.fetch_all(sql)):
        data.append({
            "ID": index + 1,
            "Department": row["学院"],
            "Course_name": row["课程名"],
            "Teacher": row["教师"],
            "Time": row["周次"],
            "Week": row["星期"],
            "Class_time": "%s~%s" % (row["开始节次"], row["开始节次"] + row["时长节次"] - 1),
            "Teaching_building": row["教学楼"],
            "Classroom": row["教室"]
        })
    return {"message": message, "error": error, "code": code, "data": data}
