from flask import request

from plugins_v3._login.login import login
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.session import session
from . import api, config


@api.route("/exam", methods=["GET"])
@check_sign({'name', 'passwd'})
@request_limit()
@need_proxy()
@cache({'name'})
def handle_exam():
    name = request.args.get('name', '')
    passwd = request.args.get('passwd', '')
    cookies = login(name, passwd)
    post_data = {
        'xqm': 3,
        'xnm': 2020,
        'queryModel.showCount': 500
    }
    items = session.post(config.exam_url, data=post_data, cookies=cookies).json()
    exam_items = []
    for item in items["items"]:
        exam_items.append({
            'type': item['ksmc'],
            'college': item['kkxy'],
            'location': item['cdmc'],
            'time': item['kssj'],
            'name': item['jxbmc']
        })
    return {
        'code': 0,
        'data': exam_items
    }
