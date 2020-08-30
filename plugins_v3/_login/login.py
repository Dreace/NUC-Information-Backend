import base64
import json
import re

import rsa

from utils.exceptions import custom_abort
from utils.redis_connections import redis_session
from utils.session import session
from . import config


def base_64_to_int(raw_str: str) -> int:
    return int.from_bytes(base64.b64decode(raw_str), 'big')


def login(name: str, passwd: str, disable_cache=False) -> dict:
    """ 使用用户名和密码登录教务系统

    :param name: 用户名（学号）
    :param passwd: 密码
    :param disable_cache: 是否禁用缓存的 cookie，首次登录时应当禁用，防止错误密码也能“登录成功”
    :return 成功登录后的 cookies
    """
    if not name or not passwd:
        custom_abort(-3, '账号密码不能为空')
    if name.strip() != name:
        custom_abort(-3, '用户名包含空字符')
    if not disable_cache:
        cookie_json = redis_session.get("cookie" + name)
        if cookie_json:
            cookies = json.loads(cookie_json)
            r = session.get(config.test_url, allow_redirects=False, cookies=cookies)
            if r.status_code == 200:
                redis_session.expire("cookie" + name, 43200)
                return cookies
            else:
                redis_session.delete("cookie" + name)
    index_response = session.get(config.index_url)
    csrf_token = re.search('name="csrftoken" value="(.*?)"', index_response.content.decode()).group(1)
    cookies = index_response.cookies.get_dict()
    public_key_dict = session.get(config.public_key_url, cookies=cookies).json()
    public_key = rsa.PublicKey(base_64_to_int(public_key_dict["modulus"]),
                               base_64_to_int(public_key_dict["exponent"]))
    post_data = {
        'csrftoken': csrf_token,
        'yhm': name,
        'mm': base64.b64encode(rsa.encrypt(passwd.encode(), public_key))
    }
    login_response = session.post(config.index_url, data=post_data, allow_redirects=False, cookies=cookies)
    if login_response.content.decode().find("不正确") != -1:
        custom_abort(-3, '账号或密码错误')
    cookies['JSESSIONID'] = login_response.cookies.get('JSESSIONID')
    redis_session.set("cookie" + name, json.dumps(cookies), ex=43200)
    return cookies
