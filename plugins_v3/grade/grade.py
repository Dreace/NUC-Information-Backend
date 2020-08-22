import json

import pika
from flask import request

import global_config
from plugins_v3._login.login import login
from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.guest import guest
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort
from . import api
from .config import *

credentials = pika.PlainCredentials(global_config.rabbitmq['username'], global_config.rabbitmq['password'])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        heartbeat=0,
        host=global_config.rabbitmq['host'],
        port=global_config.rabbitmq['port'],
        credentials=credentials
    ))
channel = connection.channel()
channel.queue_declare(queue='grade', durable=True)


@api.route('/grade', methods=['GET'])
@check_sign({'name', 'passwd'})
@request_limit()
@need_proxy()
@cache({'name'})
@guest('guest')
def handle_grade():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    session = login(name, passwd)
    post_data = {
        'xnm': '',
        'xqm': '',
        'queryModel.showCount': 1000,
    }
    grade = session.post(grade_url, post_data).json()
    grade_items = {}
    for item in grade['items']:
        dict_key = item['xnmmc'] + '-' + item['xqmmc']
        if dict_key not in grade_items:
            grade_items[dict_key] = []
        grade_items[dict_key].append({
            'name': item.get('kcmc', ''),
            'credit': float(item['xf']) if 'xf' in item else '',
            'grade': item.get('bfzcj', ''),
            'gradePoint': float(item['jd']) if 'jd' in item else '',
            'testType': item.get('kcxzmc', ''),
            'testStatus': item.get('ksxz', ''),
        })
    data = list(grade_items.values())
    g_a, g_b = 0, 0
    g_a_, g_b_ = 0, 0
    for item_i in data:
        a, b = 0, 0
        a_, b_ = 0, 0
        for item_j in item_i:
            if item_j['credit'] and item_j['gradePoint']:
                t = item_j['credit'] * item_j['gradePoint']
                a += t
                g_a += t
                b += item_j['credit']
                g_b += item_j['credit']
                if item_j['testType'] == '必修' and item_j['testStatus'] == '正常考试':
                    a_ += t
                    g_a_ += t
                    b_ += item_j['credit']
                    g_b_ += item_j['credit']
                del item_j['testType']
                del item_j['testStatus']
        if b:
            item_i.append({
                'name': '学期平均绩点',
                'gradePoint': round(a / b, 2)
            })
        if b_:
            item_i.append({
                'name': '学期平均绩点（必修）',
                'gradePoint': round(a_ / b_, 2)
            })
    if g_b:
        data[-1].append({
            'name': '总平均绩点',
            'gradePoint': round(g_a / g_b, 2)
        })
    if g_b_:
        data[-1].append({
            'name': '总平均绩点（必修）',
            'gradePoint': round(g_a_ / g_b_, 2)
        })
    return {
        'code': 0,
        'data': data
    }


@api.route('/grade/async', methods=['GET'])
@check_sign({'name', 'passwd', 'openID'})
@request_limit()
def handle_grade_async():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    open_id = request.args.get('openID', type=str)
    if not name or not passwd:
        custom_abort(-2, '账号密码不能为空')
    body = {
        'type': 'grade',
        'user': {
            'name': name,
            'passwd': passwd,
            'open_id': open_id
        }
    }
    channel.basic_publish(exchange='',
                          routing_key='grade',
                          body=json.dumps(body),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    return {
        'code': 0,
        'data': 'OK'
    }
