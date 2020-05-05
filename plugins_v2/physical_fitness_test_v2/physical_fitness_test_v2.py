import base64
import hashlib
import time

import requests
from Crypto.Cipher import AES
from flask import Response, request

from . import api
from .config import *

BS = AES.block_size  # aes数据分组长度为128 bit
key = AES.new("76a9c9f0e5ae4d2d84bf6eda1613ddbf".encode(), AES.MODE_ECB)


def pad(m):
    return (m + chr(16 - len(m) % 16) * (16 - len(m) % 16)).encode()


def sign(args: dict):
    args["appId"] = "76a9c9f0e5ae4d2d84bf6eda1613ddbf"
    args["appSecret"] = "e8167ef026cbc5e456ab837d9d6d9254"
    args_list = []
    for k in sorted(args):
        args_list.append(k + "=" + str(args[k]))
    arg = "&".join(args_list)
    del args["appId"]
    del args["appSecret"]
    return hashlib.md5(arg.encode("utf-8")).hexdigest()


@api.route('/captcha', methods=['GET'])
def handle_captcha():
    res = captcha()
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/login', methods=['GET'])
def handle_login():
    res = login(request.args)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/list', methods=['GET'])
def handle_list_grade():
    student_id = request.args.get("id", "")
    res = list_grade(student_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/detail', methods=['GET'])
def handle_grade_detail():
    grade_id = request.args.get("id", "")
    res = grade_detail(grade_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def grade_detail(grade_id):
    message = "OK"
    code = 0
    data = ""
    post_data = {
        "meaScoreId": grade_id,
        "timestamp": int(time.time() * 1000)
    }
    post_data["sign"] = sign(post_data)
    res = requests.post(grade_detail_url, proxies=proxies, data=post_data).content.decode()
    res_json = json.loads(res)
    if res_json["returnCode"] == '200':
        data = res_json["data"]
    else:
        message = res_json["returnMsg"]
        code = -1
    return {"message": message, "code": code, "data": data}


def list_grade(student_id):
    message = "OK"
    code = 0
    data = ""
    post_data = {
        "userId": student_id,
        "timestamp": int(time.time() * 1000)
    }
    post_data["sign"] = sign(post_data)
    res = requests.post(grade_list_url, proxies=proxies, data=post_data).content.decode()
    res_json = json.loads(res)
    if res_json["returnCode"] == '200':
        data = res_json["data"]
    else:
        message = res_json["returnMsg"]
        code = -1
    return {"message": message, "code": code, "data": data}


def captcha():
    message = "OK"
    code = 0
    captcha_request = requests.get(captcha_code_url, proxies=proxies)
    data = {
        "captchaBase64": base64.b64encode(captcha_request.content).decode(),
        "JSESSIONID": captcha_request.cookies.get("JSESSIONID")
    }
    return {"message": message, "code": code, "data": data}


def login(args):
    message = "OK"
    code = 0
    data = {}
    if len(args.get("name")) < 1 or len(args.get("passwd")) < 1:
        code = -2
        message = "账号密码不能为空"
    else:
        session = requests.session()
        session.proxies = proxies
        session.cookies.set("JSESSIONID", args.get("JSESSIONID"))

        post_data = {
            "uname": base64.b64encode(key.encrypt(pad(args.get("name")))).decode(),
            "pwd": base64.b64encode(key.encrypt(pad(args.get("passwd")))).decode(),
            "code": args.get("captcha"),
            "timestamp": int(time.time() * 1000)
        }
        post_data["sign"] = sign(post_data)
        login_res = json.loads(session.post(login_url, data=post_data, allow_redirects=False).content.decode())
        if login_res["returnMsg"]:
            code = 1
            message = login_res["returnMsg"]
        else:
            info_res = json.loads(session.post(info_url).content.decode())
            data = {
                "id": info_res["data"][0]["sysUser"]["id"]
            }

    return {"message": message, "code": code, "data": data}
