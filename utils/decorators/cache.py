import hashlib
import json
import logging
from functools import wraps
from urllib.parse import unquote

from flask import request

from utils.redis_connections import redis_cache


def cache(cache_args: set, expire: int = 600):
    """ 缓存请求，若命中缓存直接返回

    :param cache_args: 根据 cache_args 生成缓存唯一缓存 id
    :param expire: 缓存过期时间（秒）,默认 600 秒
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs) -> dict:
            arg_list = []
            for k in sorted(dict(request.args)):
                if k in cache_args:
                    arg_list.append(k + "=" + request.args.get(k))
            if arg_list:
                cache_key = request.path + '?' + '&'.join(arg_list)
            else:
                cache_key = request.path
            cache_key_md5 = hashlib.md5(cache_key.encode()).hexdigest()
            cached = redis_cache.get(cache_key_md5)
            if cached:
                logging.info("命中缓存 %s", unquote(cache_key))
                return json.loads(cached)
            else:
                res: dict = f(*args, **kwargs)
                if res.get('code', -1) == 0:
                    redis_cache.set(cache_key_md5, json.dumps(res), expire)
                    logging.info("缓存 %s", unquote(cache_key))
                return res

        return decorated_function

    return decorator
