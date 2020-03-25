import json

from flask import Response
from flask import request

from mysql_connect import course_cursor, course_db
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
    keywords_map = "".join(map(lambda k: "(?=.*%s)" % k, keywords.split(" ")))
    sql = "SELECT * FROM `课程-2020-1` WHERE CONCAT_WS('', `学院`, `课程名`, `教师`) REGEXP '%s^.*$'" % keywords_map
    course_db.ping(reconnect=True)
    course_cursor.execute(sql)
    data = []
    for index, row in enumerate(course_cursor.fetchall()):
        data.append({
            "ID": index + 1,
            "Department": row[1],
            "Course_name": row[2],
            "Teacher": row[3],
            "Time": row[4],
            "Week": row[5],
            "Class_time": "%s~%s" % (row[6], row[6] + row[7] - 1),
            "Teaching_building": row[8],
            "Classroom": row[9]
        })
    return {"message": message, "error": error, "code": code, "data": data}
