from functools import wraps

from utils.exceptions import custom_abort
from utils.gol import global_values


def need_proxy():
    """ 检查代理状态，若离线直接返回

    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs) -> dict:
            if not global_values.get_value("proxy_status_ok"):
                custom_abort(-2, '无法连接学校网络')
            return f(*args, **kwargs)

        return decorated_function

    return decorator
