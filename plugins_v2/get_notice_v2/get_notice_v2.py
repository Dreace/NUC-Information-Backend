import json

import pymysql
from flask import Response
from flask import request

from utils.sql_helper import SQLHelper
from . import api


@api.route('/GetNoticeList', methods=['GET'])
def handle_get_notice_list():
    res = get_notice()
    resp = Response(json.dumps(res), mimetype="application/json")
    return resp


@api.route('/GetOneNoticeContent', methods=['GET'])
def handle_get_one_notice_content():
    notice_id = int(request.args.get("id"))
    res = get_one_notice_content(notice_id)
    resp = Response(json.dumps(res), mimetype="application/json")
    return resp


@api.route('/GetNewNotice', methods=['GET'])
def handle_get_new_notice():
    res = get_new_notice()
    resp = Response(json.dumps(res), mimetype="application/json")
    return resp


def get_new_notice():
    sql = "SELECT max(id) id FROM `notice`"
    notice_id = SQLHelper.fetch_one(sql)
    res = get_one_notice_content(notice_id["id"])
    return res


def get_one_notice_content(notice_id: int):
    message = ""
    error = ""
    code = 0
    data = ""
    notice_id = pymysql.escape_string(str(notice_id))
    sql = "SELECT `内容`,`时间`,`标题`,`id`,`重要` FROM notice WHERE id = %s" % notice_id

    result = SQLHelper.fetch_one(sql)
    if result is None:
        message = "没有内容"
        error = "没有数据"
        code = -6
    else:
        data = {
            "content": result["内容"],
            "time": str(result["时间"]),
            "title": result["标题"],
            "id": result["id"],
            "importance": result["重要"]
        }
    res = {
        "message": message,
        "error": error,
        "code": code,
        "data": data
    }

    return res


def get_notice():
    message = "没有公告"
    error = "没有数据"
    code = -6
    data = ""
    sql = "SELECT * FROM `notice` "
    # 所有公告
    results = SQLHelper.fetch_all(sql)
    if len(results) >= 1:
        notices = {"top": [], "normal": []}
        message = ""
        error = ""
        code = 0
        for res in results:
            is_top = res["是否置顶"]
            notice = {
                "id": res["id"],
                "title": res["标题"],
                "time": str(res["时间"])
            }
            if is_top:
                notices["top"].append(notice)
            else:
                notices["normal"].append(notice)
        notices["top"] = list(reversed(notices["top"]))
        notices["normal"] = list(reversed(notices["normal"]))
        data = notices
    res = {
        "message": message,
        "error": error,
        "code": code,
        "data": data
    }
    return res
