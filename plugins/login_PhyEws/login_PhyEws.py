from flask import request
from flask import Response
from plugins._login_PhyEws.login_PhyEws import login_PhyEws
import json
from . import api


@api.route('/LoginPhyEws', methods=['GET'])
def handle_get_course():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = login_PhyEws_(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def login_PhyEws_(name, passwd):
    message = "登录成功"
    error = ""
    code = 0
    data = "0"
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "登陆失败"
        error = "账号密码不能为空"

    else:
        session = login_PhyEws(name, passwd)
        if type(1) == type(session):
            code = -1
            message = "登陆失败"
            if session == 2:
                error = "账号或密码错误"
            else:
                error = "服务器异常"
    return {"message": message, "error": error, "code": code, "data": data}
