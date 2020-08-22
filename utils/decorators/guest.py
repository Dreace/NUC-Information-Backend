import json
from functools import wraps

from flask import request

with open('data/guest.json', encoding='utf-8') as guest_file:
    _data = json.loads(guest_file.read())


def guest(name: str, find_in_path=False):
    """ 命中规则时返回示例数据

    :param find_in_path: 是否在 url 寻找 key_name
    :param name: 如果 name 参数匹配这个值就返回样例数据
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs) -> dict:
            if find_in_path:
                if request.path.find(name) != -1:
                    return {
                        'code': 0,
                        'data': _data.get(request.path, {})
                    }
                else:
                    return f(*args, **kwargs)
            else:
                if request.args.get('name', '') == name:
                    return {
                        'code': 0,
                        'data': _data.get(request.path, {})
                    }
                else:
                    return f(*args, **kwargs)

        return decorated_function

    return decorator
