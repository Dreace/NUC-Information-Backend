import hashlib
import logging
import time
from functools import wraps
from urllib.parse import quote

from flask import request

from global_config import app_secret
from utils.exceptions import custom_abort


def check_sign(check_args: set):
    """ 校验参数签名，sign 参数不存在直接失败，
    request.path 也将参与 sign 计算

    :param check_args: 需要参与校验的参数集合
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs) -> dict:
            if "sign" not in request.args.keys() or \
                    "ts" not in request.args.keys() or \
                    "key" not in request.args.keys():
                logging.warning('缺少参数')
                custom_abort(-2, '请求签名校验失败')
            if int(request.args["ts"]) + 3e5 < int(time.time() * 1000):
                logging.warning('{} 参数签名过期'.format(request.args['key']))
                custom_abort(-2, '参数签名过期')
            need_check_args = check_args.union({'ts', 'key'})
            arg_list = []
            for k in sorted(dict(request.args)):
                if k in need_check_args:
                    arg_list.append(k + "=" + quote(request.args[k], safe="~()*!.\'"))
            url_args = quote(request.path) + "&".join(arg_list)
            # print(url_args)
            # print(hashlib.md5((url_args + app_secret).encode("utf-8")).hexdigest())
            if request.args["sign"] != hashlib.md5((url_args + app_secret).encode("utf-8")).hexdigest():
                logging.warning('{} 请求签名校验失败'.format(request.args['key']))
                custom_abort(-2, '请求签名校验失败')
            return f(*args, **kwargs)

        return decorated_function

    return decorator
