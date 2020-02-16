import hashlib
import json
import logging
import os
import random
import re
from datetime import date, datetime
from uuid import uuid1

from dateutil.relativedelta import relativedelta
from flask import Response
from flask import request
from icalendar import Calendar, Event
from pytz import timezone
from qiniu import Auth, put_file

from .config import ical_file_path, qiniu_access_key, qiniu_secret_key

cst_tz = timezone('Asia/Shanghai')
utc_tz = timezone('UTC')
from . import api

q = Auth(qiniu_access_key, qiniu_secret_key)
bucket_name = 'blog_cdn'


@api.route('/ToiCal', methods=['POST'])
def handle_to_ical():
    arguments = request.get_json()
    data = arguments["data"]
    first_monday = arguments["firtMonday"]
    res = to_ical(data, first_monday)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def display(cal):
    return cal.to_ical().decode('utf-8').replace('\r\n', '\n').strip()


def write_ics_file(name, ics_text):
    with open(ical_file_path + name, "w", encoding='utf-8') as file:
        file.write(display(ics_text))
    key = 'files/%s' % name
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, ical_file_path + name)
    os.remove(ical_file_path + name)
    logging.debug(info)


def generate_random_str(random_length=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(random_length):
        random_str += base_str[random.randint(0, length)]
    return random_str


def to_ical(table, first_monday):
    message = "OK"
    error = ""
    code = 0
    data = {}
    rule = re.compile(r"[^a-zA-Z0-9\-,]")
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//NUC//Syllabus//CN'  # *mandatory elements* where the prodid can be changed, see RFC 5445
    mondaySplit = first_monday.split('-')
    start_monday = date(int(mondaySplit[0]), int(mondaySplit[1]), int(mondaySplit[2]))  # 开学第一周星期一的时间
    dict_day = {1: relativedelta(hours=8, minutes=0), 3: relativedelta(hours=10, minutes=10),
                5: relativedelta(hours=14, minutes=30), 7: relativedelta(hours=16, minutes=40),
                9: relativedelta(hours=19, minutes=30)}
    dict_day2 = {1: relativedelta(hours=8, minutes=0), 3: relativedelta(hours=10, minutes=10),
                 5: relativedelta(hours=14, minutes=0), 7: relativedelta(hours=16, minutes=10),
                 9: relativedelta(hours=19, minutes=0)}
    for i in table:
        if "Course_Week" not in i:
            continue
        for j in rule.sub('', i["Course_Week"]).split(','):
            if j.find('-') != -1:
                d = j.split('-')
                for dday in range(int(d[0]), int(d[1]) + 1):
                    event = Event()
                    dtstart_date = start_monday + relativedelta(
                        weeks=(dday - 1)) + relativedelta(days=int(int(i["Course_Time"])) - 1)
                    dtstart_datetime = datetime.combine(dtstart_date, datetime.min.time())
                    if dtstart_date.month >= 5 and dtstart_date.month < 10:
                        dtstart = dtstart_datetime + dict_day[int(i["Course_Start"])]
                    else:
                        dtstart = dtstart_datetime + dict_day2[int(i["Course_Start"])]
                    dtend = dtstart + relativedelta(hours=1, minutes=40)
                    event.add('X-WR-TIMEZONE', 'Asia/Shanghai')
                    event.add('uid', str(uuid1()) + '@Dreace')
                    event.add('summary', i["Course_Name"])
                    event.add('dtstamp', datetime.now())
                    event.add('dtstart', dtstart.replace(tzinfo=cst_tz).astimezone(cst_tz))
                    event.add('dtend', dtend.replace(tzinfo=cst_tz).astimezone(cst_tz))
                    event.add('rrule',
                              {'freq': 'weekly', 'interval': 1,
                               'count': 1})
                    event.add('location', i["Course_Building"] + i["Course_Classroom"])
                    cal.add_component(event)
            else:
                if j == '':
                    continue
                event = Event()
                dtstart_date = start_monday + relativedelta(
                    weeks=(int(j) - 1)) + relativedelta(days=int(int(i["Course_Time"])) - 1)
                dtstart_datetime = datetime.combine(dtstart_date, datetime.min.time())
                if dtstart_date.month >= 5 and dtstart_date.month < 10:
                    dtstart = dtstart_datetime + dict_day[int(i["Course_Start"])]
                else:
                    dtstart = dtstart_datetime + dict_day2[int(i["Course_Start"])]
                dtend = dtstart + relativedelta(hours=1, minutes=40)
                event.add('X-WR-TIMEZONE', 'Asia/Shanghai')
                event.add('uid', str(uuid1()) + '@Dreace')
                event.add('summary', i["Course_Name"])
                event.add('dtstamp', datetime.now())
                event.add('dtstart', dtstart.replace(tzinfo=cst_tz).astimezone(cst_tz))
                event.add('dtend', dtend.replace(tzinfo=cst_tz).astimezone(cst_tz))
                event.add('rrule',
                          {'freq': 'weekly', 'interval': 1,
                           'count': 1})
                event.add('location', i["Course_Building"] + i["Course_Classroom"])
                cal.add_component(event)
    filename = hashlib.md5(json.dumps(table).encode('utf8')).hexdigest().upper() + ".ics"

    write_ics_file(filename, cal)
    data["url"] = "https://blog-cdn.dreace.top/files/" + filename
    return {"message": message, "error": error, "code": code, "data": data}
