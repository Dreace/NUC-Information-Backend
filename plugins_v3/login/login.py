# coding=utf-8

from flask import request

from plugins_v3._login.login import login
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from . import api


@api.route('/login', methods=['GET'])
@check_sign(check_args={'name', 'passwd'})
@request_limit()
@need_proxy()
def handle_login():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    login(name, passwd, True)
    return {
        'code': 0,
        'message': 'OK'
    }
