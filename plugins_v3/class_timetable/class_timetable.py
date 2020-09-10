import logging

from global_config import NAME, PASSWD
from plugins_v3._login.login import login
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort, CustomHTTPException
from utils.session import session
from . import api, config


@api.route('/classTimetable/<string:class_name>', methods=['GET'])
@check_sign(set())
@request_limit()
@need_proxy()
@cache(set())
def handle_class_timetable(class_name: str):
    if not class_name:
        custom_abort(-6, '空关键词')
    cookies = {}
    try:
        cookies = login(NAME, PASSWD)
    except CustomHTTPException:
        logging.warning('全局账号登录失败')
        custom_abort(-6, '查询失败')
    post_data = {
        'xnm': '2019',
        'xqm': '12',
        'xqh_id': '01',
        'njdm_id': '',
        'jg_id': '',
        'zyh_id': '',
        'zyfx_id': '',
        'bh_id': class_name,
        '_search': 'false',
        'queryModel.showCount': '1',
    }
    pre_data_json = session.post(config.pre_class_timetable_url, data=post_data, cookies=cookies).json()
    if not pre_data_json['items']:
        custom_abort(-6, '无效的班级号')
    post_data = {
        'xnm': '2020',
        'xqm': '3',
        'xnmc': '2020-2021',
        'xqmmc': '1',
        'xqh_id': '01',
        'njdm_id': pre_data_json['items'][0]['njdm_id'],
        'zyh_id': pre_data_json['items'][0]['zyh_id'],
        'bh_id': class_name,
        'tjkbzdm': '1',
        'tjkbzxsdm': '0',
        # 'zxszjjs': True
    }
    timetable = session.post(config.class_timetable_url, data=post_data, cookies=cookies).json()
    timetable_items = []
    cnt = 0
    name_dict = {}
    for index, table in enumerate(timetable['kbList']):
        spited = table['jcor'].split('-')
        if table['kcmc'] not in name_dict:
            name_dict[table['kcmc']] = cnt
            cnt += 1
        timetable_items.append({
            'name': table.get('kcmc', ''),
            'teacher': table.get('xm'),
            # 哪几周上课，形如”9-14周“
            'weeks': table.get('zcd', ''),
            'color': name_dict[table['kcmc']],
            # 星期几
            'dayOfWeek': table.get('xqj', ''),
            # 第几小节开始
            'start': int(spited[0]),
            # 上几小节
            'length': int(spited[1]) - int(spited[0]) + 1,
            'building': table.get('xqmc'),
            'classroom': table.get('cdmc')
        })
    for d in timetable['sjkList']:
        timetable_items.append({
            'name': d['sjkcgs']
        })
    return {
        'code': 0,
        'data': timetable_items
    }
