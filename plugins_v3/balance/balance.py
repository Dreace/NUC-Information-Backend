# coding=utf-8
import datetime
from datetime import datetime

import bs4
import pytz
import requests

from global_config import proxies
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.guest import guest
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort
from . import api, config

cst_tz = pytz.timezone('Asia/Shanghai')


@api.route('/balance/<string:name>', methods=['GET'])
@check_sign(set())
@request_limit()
@cache(set())
@guest('guest', True)
def handle_balance(name: str):
    session = requests.session()
    session.proxies = proxies
    session.get(config.url1)
    time_now = datetime.now(cst_tz)
    local_time_hour = time_now.timetuple()[3]
    if local_time_hour >= 22 or local_time_hour <= 1:
        custom_abort(-6, '非服务时间')
    post_data = {
        'pageMark': '3',
        'paymentContent': 'busiCode=%s' % name,
        'queryPageinfo': '1',
        'netType': '181',
        'IEVersionFlag': 'ANDROID-CHROME-0',
        'ComputID': '98',
        'PlatFlag': '8',
        'areaCodeTmp': '0502',
        'areaNameTmp': '̫ԭ',
        'dse_menuid': 'PM002',
        'IN_PAYITEMCODE': 'PJ120012021000010048',
        'cmd': '',
        'isShortpay': '',
        'maskFlag': '0',
        'isP3bank': '0'
    }
    content = session.post(config.url2, data=post_data).content
    soups = bs4.BeautifulSoup(content, 'html.parser')
    balance = soups.find(id='item37')
    name = soups.find(id='item31')
    if not balance:
        custom_abort(-6, '没有数据')
    return {
        'code': 0,
        'data': {
            'balance': balance.text,
            'name': name.text,
            'time': time_now.strftime('%Y-%m-%d %H:%M')
        }
    }
