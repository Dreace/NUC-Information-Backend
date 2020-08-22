from functools import wraps

from utils.exceptions import custom_abort


def stopped():
    """ 已停止服务，直接返回

    """

    def decorator(f):
        @wraps(f)
        def decorated_function():
            custom_abort(-4, '未开发查询')

        return decorated_function

    return decorator
