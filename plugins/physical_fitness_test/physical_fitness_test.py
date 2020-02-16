# coding=utf-8
import hashlib
import json
import logging
import ssl
import time

import requests
from flask import Response
from flask import request

from . import api
from .config import app, login_url, headers, mea_score_id_url, score_detail_url, proxies

ssl._create_default_https_context = ssl._create_unverified_context


@api.route('/PhysicalFitnessTestLogin', methods=['GET'])
def handle_physical_fitness_test_login():
    name = request.args.get('name')
    pwd = request.args.get('passwd')
    res = login(name, pwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/PhysicalFitnessTestGetScoreList', methods=['GET'])
def handle_physical_fitness_test_get_score_list():
    id_ = request.args.get('id')
    res = get_score_list(id_)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/PhysicalFitnessTestGetScore', methods=['GET'])
def handle_physical_fitness_test_get_score():
    id_ = request.args.get('id')
    res = get_score(id_)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def login(name, pwd):
    message = "登录成功"
    error = ""
    code = 0
    data = "0"
    time_now = int(round(time.time() * 1000))
    url_data = "%spwd=%s&timestamp=%s&uname=%s" % (app, pwd, time_now, name)
    sign = hashlib.md5(url_data.encode()).hexdigest()
    url_data = "pwd=%s&sign=%s&timestamp=%s&uname=%s" % (pwd, sign, time_now, name)
    res = requests.post(login_url, data=url_data, headers=headers, proxies=proxies).content
    res_json = json.loads(res)
    if res_json["returnCode"] == '200':
        data = res_json["data"]
    else:
        message = res_json["returnMsg"]
        code = -1
    return {"message": message, "error": error, "code": code, "data": data}


def get_score_list(id_):
    message = "OK"
    error = ""
    code = 0
    data = "0"
    time_now = int(round(time.time() * 1000))
    url_data = "%stimestamp=%s&userId=%s" % (app, time_now, id_)
    sign = hashlib.md5(url_data.encode()).hexdigest()
    url_data = "sign=%s&timestamp=%s&userId=%s" % (sign, time_now, id_)
    res = requests.post(mea_score_id_url, data=url_data, headers=headers, proxies=proxies).content
    res_json = json.loads(res)
    if res_json["returnCode"] == '200':
        data = res_json["data"]
    else:
        message = res_json["returnMsg"]
        code = -1
    return {"message": message, "error": error, "code": code, "data": data}


def get_score(id_):
    message = "OK"
    error = ""
    code = 0
    data = "0"
    time_now = int(round(time.time() * 1000))
    url_data = "%s&meaScoreId=%s&timestamp=%s" % (app, id_, time_now)
    sign = hashlib.md5(url_data.encode()).hexdigest()
    url_data = "sign=%s&meaScoreId=%s&timestamp=%s" % (sign, id_, time_now,)
    res = requests.post(score_detail_url, data=url_data, headers=headers, proxies=proxies).content
    res_json = json.loads(res)
    if res_json["returnCode"] == '200':
        data = res_json["data"]
    else:
        message = res_json["returnMsg"]
        code = -1
    return {"message": message, "error": error, "code": code, "data": data}
