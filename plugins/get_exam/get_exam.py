import json

from flask import Response
from flask import request

from utils.sql_helper import SQLHelper
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
        results = SQLHelper.fetch_all(sql[:-4])
        for row in results:
            r = {
                "course_name": row[2],
                "time": row[3],
                "date": row[4],
                "class": row[5],
                "classroom": row[6]
            }
            # TODO 若重新启用，把上面改为列名
            data.append(r)
        for j in keywords.split()[1:]:
            a = []
            for i in data:
                if i["course_name"].find(j) != -1 or i["class"].find(j) != -1:
                    a.append(i)
            data = a
    return {"message": message, "error": error, "code": code, "data": data}
