import base64
import json
import re

import requests
import rsa

from global_config import proxies
from utils.exceptions import custom_abort
from utils.redis_connections import redis_session
from .config import index_url, public_key_url, test_url


def base_64_to_int(raw_str: str) -> int:
    return int.from_bytes(base64.b64decode(raw_str), 'big')


def login(name: str, passwd: str, disable_cache=False) -> requests.Session:
    """ 使用用户名和密码登录教务系统

    :param name: 用户名（学号）
    :param passwd: 密码
    :param disable_cache: 是否禁用缓存的 cookie，首次登录时应当禁用，防止错误密码也能“登录成功”
    :return 成功登录后的 requests.Session
    """
    if not name or not passwd:
        custom_abort(-3, '账号密码不能为空')
    if name.strip() != name:
        custom_abort(-3, '用户名包含空字符')
    session = requests.session()
    session.proxies = proxies
    if not disable_cache:
        cookie_json = redis_session.get("cookie" + name)
        if cookie_json:
            session.cookies.update(json.loads(cookie_json))
            r = session.get(test_url, allow_redirects=False)
            if r.status_code == 200:
                redis_session.expire("cookie" + name, 3600)
                return session
            else:
                redis_session.delete("cookie" + name)
    index_html = session.get(index_url).content.decode()
    csrf_token = re.search('name="csrftoken" value="(.*?)"', index_html).group(1)
    public_key_dict = session.get(public_key_url).json()
    public_key = rsa.PublicKey(base_64_to_int(public_key_dict["modulus"]),
                               base_64_to_int(public_key_dict["exponent"]))
    post_data = {
        'csrftoken': csrf_token,
        'yhm': name,
        'mm': base64.b64encode(rsa.encrypt(passwd.encode(), public_key))
    }
    login_html = session.post(index_url, data=post_data).content.decode()
    if login_html.find("不正确") != -1:
        custom_abort(-3, '账号或密码错误')
    redis_session.set("cookie" + name, json.dumps(session.cookies.get_dict()), ex=3600)
    return session
