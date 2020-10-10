import re

from flask import request

from plugins_v3._login.login import login
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.guest import guest
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.session import session
from . import api, config


@api.route('/timetable', methods=['GET'])
@check_sign({'name', 'passwd'})
@request_limit()
@need_proxy()
@cache({'name'})
@guest('guest')
def handle_timetable():
    name = request.args.get('name', '')
    passwd = request.args.get('passwd', '')
    cookies = login(name, passwd)
    post_data = {
        'xnm': 2020,
        'xqm': 3
    }
    timetable = session.post(config.timetable_url, data=post_data, cookies=cookies).json()
    return {
        'code': 0,
        'data': build_timetable_items(timetable)
    }


@api.route('/timetable/all', methods=['GET'])
@check_sign({'name', 'passwd'})
@request_limit()
@need_proxy()
@cache({'name'})
@guest('guest')
def handle_timetable_all():
    name = request.args.get('name', '')
    passwd = request.args.get('passwd', '')
    cookies = login(name, passwd)
    all_timetable = []
    for data in config.term_list:
        post_data = data['postData']
        name = data['name']
        timetable = session.post(config.timetable_url, data=post_data, cookies=cookies).json()
        if len(timetable["kbList"]) == 0:
            continue
        info = {
            'name': name,
            'timetable': build_timetable_items(timetable)
        }
        all_timetable.append(info)
    return {
        'code': 0,
        'data': all_timetable
    }


def build_timetable_items(timetable):
    timetable_items = []
    cnt = 0
    name_dict = {}
    for index, table in enumerate(timetable['kbList']):
        spited = table['jcor'].split('-')
        if table['kcmc'] not in name_dict:
            name_dict[table['kcmc']] = cnt
            cnt += 1
        time = table.get('kcxszc')
        s = re.findall("\d+", time)
        theory_time = 0
        if len(s) >= 1:
            theory_time = s[0]
        practice_time = 0
        if len(s) >= 2:
            practice_time = s[1]
        timetable_items.append({
            'id': table.get('kch_id', ''),
            'credit': table.get('xf', ''),
            'testType': table.get('khfsmc', ''),
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
            'classroom': table.get('cdmc'),
            'examForm': table.get('khfsmc'),
            'theoryTime': theory_time,
            'practiceTime': practice_time
        })
    for d in timetable['sjkList']:
        timetable_items.append({
            'name': d['sjkcgs']
        })
    return timetable_items
