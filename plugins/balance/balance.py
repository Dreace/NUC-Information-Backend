# coding=utf-8
import datetime
import json

from datetime import datetime
import pytz
import requests
from plugins.balance import config
import ssl
import bs4
from flask import request
from flask import Response
from .config import proxies
from flask import current_app
from . import api

ssl._create_default_https_context = ssl._create_unverified_context

post_data = config.post_data


@api.route('/CardBalance', methods=['GET'])
def handle_balance():
    student_code = request.args.get('name')
    balance = get_balance(student_code)
    resp = Response(json.dumps(balance), mimetype='application/json')
    return resp


def get_balance(student_code):
    message = "OK"
    error = ""
    code = 0
    balance_data = "0"
    name_data = "未知"
    cst_tz = pytz.timezone('Asia/Shanghai')
    time_now = datetime.now(cst_tz)
    local_time_hour = time_now.timetuple()[3]
    if local_time_hour >= 22 or local_time_hour <= 1:
        message = "非服务时间"
        error = "非服务时间"
        code = -1
    else:
        session = requests.session()
        session.proxies = proxies
        session.get(config.url1)
        post_data["paymentContent"] = "busiCode=%s" % student_code
        content = session.post(config.url2, data=config.post_data).content
        soups = bs4.BeautifulSoup(content, "html.parser")
        balance = soups.find_all(id="item37")
        name = soups.find_all(id="item31")
        if len(balance) < 1:
            message = "没有数据"
            error = "没有数据"
            code = -1
        else:
            balance_data = balance[0].text
            if len(name) > 0:
                name_data = name[0].text
    res = {
        "message": message,
        "error": error,
        "code": code,
        "data": {
            "balance": balance_data,
            "name": name_data,
            "time": time_now.strftime("%Y-%m-%d %H:%M")
        }
    }
    return res
