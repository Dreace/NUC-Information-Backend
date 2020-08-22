import logging
import time
from functools import wraps

from flask import request

from utils.exceptions import custom_abort
from utils.redis_connections import redis_request_limit


def request_limit(limit_per_minute: int = 10):
    """ 每分钟请求限制

    :param limit_per_minute: 每分钟请求限制数
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs) -> dict:
            user_key = request.args['key'] + request.path
            if redis_request_limit.llen(user_key) < limit_per_minute:
                redis_request_limit.lpush(user_key, time.time())
            else:
                first_time = redis_request_limit.lindex(user_key, -1)
                if time.time() - float(first_time) < 60:
                    logging.warning("{} 达到请求限制（{}次/分钟）".format(request.args['key'], 10))
                    custom_abort(-5, '操作过频繁')
                else:
                    redis_request_limit.lpush(user_key, time.time())
                    redis_request_limit.ltrim(user_key, 0, limit_per_minute - 1)
            redis_request_limit.expire(user_key, 60)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
