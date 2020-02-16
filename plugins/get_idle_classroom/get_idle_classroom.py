import json
import logging

from flask import Response
from flask import request

from mysql_connect import classroom_cursor as cursor, classroom_db as db
from . import api


@api.route('/GetIdleClassroom', methods=['GET'])
def handle_get_idle_classroom():
    building = request.args.get('building', "")
    class_with_week = request.args.get('class', "")
    week = request.args.get('week', "")
    res = get_idle_classroom_list(building, class_with_week, week)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetBuildingList', methods=['GET'])
def handle_get_building_list():
    res = get_building_list()
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_building_list():
    message = "OK"
    error = ""
    code = 0
    data = [u"一号楼", u"四号楼", u"六号楼", u"七号楼", u"八号楼", u"九号楼", u"十号楼", u"十一号楼", u"十四号楼", u"十五号楼",
            u"十六号楼", u"旧一号楼", u"语音", u"其他"]
    return {"message": message, "error": error, "code": code, "data": data}


def get_idle_classroom_list(building, class_with_week, week):
    message = "OK"
    error = ""
    code = 0
    data = []
    if str.isdigit(week[1:]) and int(week[1:]) <= 20:
        args = (building, class_with_week, week)
        sql = "select * from idle_classroom where building = '%s' and class_with_week = '%s' and `%s` = 1" % args
        db.ping(reconnect=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            data.append(row[2])
    return {"message": message, "error": error, "code": code, "data": data}
