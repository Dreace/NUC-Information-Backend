import json

from flask import Response
from flask import request

from utils.redis_connections import redis_news
from . import api


@api.route('/GetNews', methods=['GET'])
def handle_get_news():
    op = request.args.get('op', "")
    page = request.args.get('page', "1")
    id = request.args.get('id', "")
    type_id = request.args.get('type', "")
    res = get_news(op, int(page), id, type_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


# type_dic = {"1013": "zbxw", "1014": "tzgg", "1354": "xshd"}
name_dic = {"1013": "news", "1014": "notice", "1354": "academic"}


def get_news(op, page, id_, type_id):
    message = "OK"
    error = ""
    code = 0
    data = []
    type_name = name_dic[type_id]
    if op == "1":
        cnt = redis_news.llen(type_name + "_list")
        data = {"count": cnt}
    elif op == "2":
        page -= 1
        news_list = redis_news.lrange(type_name + "_list", page * 15, page * 15 + 14)
        new_list = []
        for i in news_list:
            new_list.append(json.loads(i))
        data = new_list
    elif op == "3":
        data = json.loads(redis_news.get(type_name + id_))
    return {"message": message, "error": error, "code": code, "data": data}
