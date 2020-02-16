import json

from flask import Response
from flask import request

from mysql_connect import exam_cursor as cursor, exam_db as db
from . import api


@api.route('/GetExam', methods=['GET'])
def handle_get_exam():
    keywords = request.args.get('keywords', "")
    res = get_exam(keywords)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_exam(keywords):
    message = "OK"
    error = ""
    code = 0
    data = []
    names = ["course_name", "class"]
    sql = "SELECT * FROM `exam` WHERE "
    for j in names:
        args = (j, keywords.split()[0])
        sql += "`%s` LIKE '%%%s%%' OR " % (args)
    if sql.find("OR") != 0:
        db.ping(reconnect=True)
        cursor.execute(sql[:-4])
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            r = {
                "course_name": row[2],
                "time": row[3],
                "date": row[4],
                "class": row[5],
                "classroom": row[6]
            }
            data.append(r)
        for j in keywords.split()[1:]:
            a = []
            for i in data:
                if i["course_name"].find(j) != -1 or i["class"].find(j) != -1:
                    a.append(i)
            data = a
    return {"message": message, "error": error, "code": code, "data": data}
