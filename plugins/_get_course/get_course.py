from flask import request
from flask import Response
from mysql_connect import course_cursor as cursor,course_db as db
import json
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
    names = ["Department", "Course_name", "Teacher"]
    sql = "SELECT * FROM `all` WHERE "
    for j in names:
        args = (j, keywords.split()[0])
        sql += "`%s` LIKE '%%%s%%' OR " % (args)
    if sql.find("OR") != 0:
        db.ping(reconnect=True)
        cursor.execute(sql[:-4])
        # 获取所有记录列表
        results = cursor.fetchall()
        i = 1
        for row in results:
            r = {
                "ID": i,
                "Department": row[1][1:],
                "Course_number": row[2][1:],
                "Course_name": row[3][1:],
                "Teacher": row[4][1:],
                "Time": row[5][1:],
                "Week": row[6][1:],
                "Class_time": row[7][1:],
                "Teaching_building": row[8][1:],
                "Classroom": row[9][1:]
            }
            i += 1
            data.append(r)
        for j in keywords.split()[1:]:
            a = []
            for i in data:
                if i["Department"].find(j) != -1 or i["Course_name"].find(j) != -1 or i["Teacher"].find(j) != -1:
                    a.append(i)
            data = a
        for i in range(len(data)):
            data[i]["ID"] = i + 1
    return {"message": message, "error": error, "code": code, "data": data}
