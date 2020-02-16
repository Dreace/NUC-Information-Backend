# coding=utf-8
import json

from flask import Response
from flask import request

from plugins_v2._login_v2.login_v2 import login
from . import api


@api.route('/Login', methods=['GET'])
def handle_login():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = login_(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def login_(name, passwd):
    message = "登录成功"
    code = 0
    data = "0"
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
    if name.strip() != name:
        code = -1
        message = "用户名包含空字符"
    else:
        session = login(name, passwd, True)
        if isinstance(session, str):
            code = -3
            message = session
    return {"message": message, "code": code, "data": data}
