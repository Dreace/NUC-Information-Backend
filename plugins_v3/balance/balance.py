# coding=utf-8
from datetime import datetime

import pytz
from flask import request

from plugins_v3._login.login import login
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.guest import guest
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort
from utils.session import session
from . import api
from .config import odd_fare_url

cst_tz = pytz.timezone('Asia/Shanghai')


@api.route('/balance', methods=['GET'])
@check_sign({'name', 'passwd'})
@request_limit()
@cache({'name'})
@guest('guest', True)
def handle_balance():
    name = request.args.get('name', '')
    passwd = request.args.get('passwd', '')
    time_now = datetime.now(cst_tz)
    cookies = login(name, passwd, all_cookies=False)
    return {
        'code': 0,
        'data': {
            'balance': session.get(odd_fare_url, cookies=cookies).json()['data']['oddfare'],
            'time': time_now.strftime('%Y-%m-%d %H:%M')
        }
    }


@api.route('/balance/<string:name>', methods=['GET'])
def temp(name: str):
    custom_abort(-1, "服务器升级中")
    pass
