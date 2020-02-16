# coding=utf-8
import json

from flask import Response
from flask import request

from plugins._login.login import login
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
    error = ""
    code = 0
    data = "0"
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        error = "登陆失败"
        message = "账号密码不能为空"

    else:
        session = login(name, passwd, True)
        if type(1) == type(session):
            code = -1
            error = "登陆失败"
            if session == 2:
                message = "账号或密码错误"
            else:
                message = "服务器异常"
    return {"message": message, "error": error, "code": code, "data": data}
