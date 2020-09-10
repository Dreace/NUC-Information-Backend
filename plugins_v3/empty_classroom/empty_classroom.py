from global_config import NAME, PASSWD
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.session import session
from . import api, config
from .._login.login import login


@api.route("/emptyClassroom/<string:building_id>/<int:week_of_term>/<int:day_of_week>/<int:class_of_day>",
           methods=['GET'])
@cache(set())
@request_limit()
@need_proxy()
@check_sign(set())
def handle_empty_classroom(building_id: str, week_of_term: int, day_of_week: int, class_of_day: int):
    cookies = login(NAME, PASSWD)

    post_data = {
        "fwzt": "cx",  # 查询
        "xnm": "2020",  # 学年
        "xqm": "3",
        "lh": building_id,  # 楼号
        "jyfs": "0",  # 教育方式？？？
        "zcd": 2 ** (week_of_term - 1),  # zcd = 2**周次-1
        "xqj": day_of_week,  # 星期几
        "jcd": 2 ** (class_of_day - 1),  # jcd = 2**节次-1
        "queryModel.showCount": "1001"
    }

    items = session.post(config.empty_classroom_url, post_data, cookies=cookies).json()
    items = items["items"]
    data = []
    for item in items:
        room = {
            "location": item["cdlbmc"],
            "roomId": item["cdmc"],
            "seats": item["zws"]
        }
        if "bz" in item.keys():
            room["seatType"] = item["bz"]
        else:
            room["seatType"] = "正常座椅"
        data.append(room)

    return {
        'code': 0,
        'data': data
    }
