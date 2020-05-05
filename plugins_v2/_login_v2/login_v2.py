import base64
import pickle
import re

import requests
import rsa

from global_config import proxies
from utils.redis_connections import redis_session
from .config import index_url, public_key_url, test_url


def base_64_to_int(raw_str: str) -> int:
    return int.from_bytes(base64.b64decode(raw_str), 'big')


def login(name, passwd, disable_cache=False):
    session = requests.session()
    session.proxies = proxies
    if not disable_cache:
        cookies_decoded = redis_session.get("cookies" + name)
        if cookies_decoded:
            session.cookies = pickle.loads(cookies_decoded.encode('latin1'))
            r = session.get(test_url, allow_redirects=False)
            if r.status_code == 200:
                redis_session.expire("cookies" + name, 3600)
                return session
            else:
                redis_session.delete("cookies" + name)
    index_html = session.get(index_url).content.decode()
    csrf_token = re.search('name="csrftoken" value="(.*?)"', index_html).group(1)
    public_key_dict = session.get(public_key_url).json()
    public_key = rsa.PublicKey(base_64_to_int(public_key_dict["modulus"]), base_64_to_int(public_key_dict["exponent"]))
    post_data = {
        'csrftoken': csrf_token,
        'yhm': name,
        'mm': base64.b64encode(rsa.encrypt(passwd.encode(), public_key))
    }
    login_html = session.post(index_url, data=post_data).content.decode()
    if login_html.find("不正确") != -1:
        return "账号或密码错误"
    else:
        redis_session.set("cookies" + name, pickle.dumps(session.cookies).decode('latin1'), ex=3600)
        return session
