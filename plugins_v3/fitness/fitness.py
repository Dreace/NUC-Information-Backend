import base64
import hashlib
import time

from Crypto.Cipher import AES
from flask import request

from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort
from utils.session import session
from . import api, config

BS = AES.block_size  # aes数据分组长度为128 bit
key = AES.new('76a9c9f0e5ae4d2d84bf6eda1613ddbf'.encode(), AES.MODE_ECB)


def pad(m):
    return (m + chr(16 - len(m) % 16) * (16 - len(m) % 16)).encode()


def sign(args: dict) -> str:
    args['appId'] = '76a9c9f0e5ae4d2d84bf6eda1613ddbf'
    args['appSecret'] = 'e8167ef026cbc5e456ab837d9d6d9254'
    args_list = []
    for k in sorted(args):
        args_list.append(k + '=' + str(args[k]))
    arg = '&'.join(args_list)
    del args['appId']
    del args['appSecret']
    return hashlib.md5(arg.encode('utf-8')).hexdigest()


@api.route('/fitness/captcha', methods=['GET'])
@check_sign(set())
@request_limit()
@need_proxy()
def handle_captcha():
    captcha_response = session.get(config.captcha_code_url)
    return {
        'code': 0,
        'data': {
            'captchaBase64': base64.b64encode(captcha_response.content).decode(),
            'JSESSIONID': captcha_response.cookies.get('JSESSIONID')
        }
    }


@api.route('/fitness/login', methods=['GET'])
@check_sign({'name', 'passwd', 'JSESSIONID', 'captcha'})
@request_limit()
@need_proxy()
def handle_login():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    if not name or not passwd:
        custom_abort(-2, '账号密码不能为空')

    post_data = {
        'uname': base64.b64encode(key.encrypt(pad(name))).decode(),
        'pwd': base64.b64encode(key.encrypt(pad(passwd))).decode(),
        'code': request.args.get('captcha', type=str),
        'timestamp': int(time.time() * 1000)
    }
    post_data['sign'] = sign(post_data)
    login_resp = session.post(config.login_url, data=post_data, allow_redirects=False,
                              cookies={'JSESSIONID': request.args.get('JSESSIONID', type=str)})
    login_res = login_resp.json()
    if login_res['returnMsg']:
        custom_abort(1, login_res['returnMsg'])
    info_res = session.post(config.info_url, cookies=login_resp.cookies.get_dict()).json()
    return {
        'code': 0,
        'data': {
            'id': info_res['data'][0]['sysUser']['id']
        }
    }


@api.route('/fitness/<user_id>', methods=['GET'])
@check_sign(set())
@request_limit(15)
@need_proxy()
@cache(set(), 1800)
def handle_list_grade(user_id: int):
    post_data = {
        'userId': user_id,
        'timestamp': int(time.time() * 1000)
    }
    post_data['sign'] = sign(post_data)
    res_json = session.post(config.grade_list_url, data=post_data).json()
    if res_json['returnCode'] != '200':
        custom_abort(-1, res_json['returnMsg'])
    return {
        'code': 0,
        'data': res_json['data']
    }


@api.route('/fitness/grade/<int:grade_id>', methods=['GET'])
@check_sign(set())
@request_limit()
@need_proxy()
@cache(set(), 1800)
def handle_grade_detail(grade_id: int):
    post_data = {
        'meaScoreId': grade_id,
        'timestamp': int(time.time() * 1000)
    }
    post_data['sign'] = sign(post_data)
    res_json = session.post(config.grade_detail_url, data=post_data).json()
    if res_json['returnCode'] != '200':
        custom_abort(-1, res_json['returnMsg'])
    return {
        'code': 0,
        'data': res_json['data']
    }
