import hashlib
import json
import os
import re
from datetime import datetime
from uuid import uuid1

from dateutil.relativedelta import relativedelta
from flask import request
from icalendar import Calendar, Event
from pytz import timezone
from qiniu import Auth, put_file

from global_config import qiniu
from utils.decorators.check_sign import check_sign
from utils.decorators.request_limit import request_limit
from . import api

cst_tz = timezone('Asia/Shanghai')
utc_tz = timezone('UTC')

q = Auth(qiniu['access_key'], qiniu['secret_key'])
bucket_name = 'blog_cdn'
with open('static/firstWeekDateTime') as file:
    first_week = file.read()


@api.route('/timetable/export', methods=['POST'])
@check_sign(set())
@request_limit()
def handle_to_ical():
    arguments: dict = request.get_json()
    timetable = arguments["timetable"]
    first_monday = arguments.get("firstWeekDateTime", first_week)
    rule = re.compile(r"[^a-zA-Z0-9\-,]")
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//NUC//Syllabus//CN'  # *mandatory elements* where the prodid can be changed, see RFC 5445
    start_monday = datetime.strptime(first_monday, '%Y/%m/%d %H:%M:%S').date()  # 开学第一周星期一的时间
    dict_day = {1: relativedelta(hours=8, minutes=0), 3: relativedelta(hours=10, minutes=10),
                5: relativedelta(hours=14, minutes=30), 7: relativedelta(hours=16, minutes=40),
                9: relativedelta(hours=19, minutes=30)}
    dict_day2 = {1: relativedelta(hours=8, minutes=0), 3: relativedelta(hours=10, minutes=10),
                 5: relativedelta(hours=14, minutes=0), 7: relativedelta(hours=16, minutes=10),
                 9: relativedelta(hours=19, minutes=0)}
    for item in timetable:
        if "weeks" not in item:
            continue
        days = []
        for j in item["weeks"].split(','):
            if j.find('-') != -1:
                is_odd = j.find("单") != -1
                is_even = j.find("双") != -1
                d = rule.sub('', j).split('-')
                for k in range(int(d[0]), int(d[1]) + 1):
                    if is_even and k % 2 == 1:
                        continue
                    if is_odd and k % 2 == 0:
                        continue
                    days.append(k)
            else:
                if not j:
                    continue
                else:
                    days.append(int(rule.sub('', j)))
        for day in days:
            event = Event()
            dtstart_date = start_monday + relativedelta(
                weeks=(day - 1)) + relativedelta(days=int(int(item["dayOfWeek"])) - 1)
            dtstart_datetime = datetime.combine(dtstart_date, datetime.min.time())
            if 5 <= dtstart_date.month < 10:
                dtstart = dtstart_datetime + dict_day[int(item["start"])]
            else:
                dtstart = dtstart_datetime + dict_day2[int(item["start"])]
            dtend = dtstart + relativedelta(hours=1, minutes=40)
            event.add('X-WR-TIMEZONE', 'Asia/Shanghai')
            event.add('uid', str(uuid1()) + '@Dreace')
            event.add('summary', item["name"])
            event.add('dtstamp', datetime.now())
            event.add('dtstart', dtstart.replace(tzinfo=cst_tz).astimezone(cst_tz))
            event.add('dtend', dtend.replace(tzinfo=cst_tz).astimezone(cst_tz))
            event.add('rrule',
                      {'freq': 'weekly', 'interval': 1,
                       'count': 1})
            event.add('location', item["building"] + item["classroom"])
            cal.add_component(event)
    filename = hashlib.md5(json.dumps(timetable).encode('utf8')).hexdigest().upper() + ".ics"

    path_name = "./files/" + filename
    with open(path_name, "w", encoding='utf-8') as file:
        file.write(cal.to_ical().decode())
    key = 'files/%s' % filename
    token = q.upload_token(bucket_name, key, 3600)
    put_file(token, key, path_name)
    os.remove(path_name)

    return {
        'code': 0,
        'data': {
            'url': "https://blog-cdn.dreace.top/files/" + filename
        }
    }
