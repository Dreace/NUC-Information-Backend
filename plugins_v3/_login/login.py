import pickle
import re

import execjs
from requests import Response
from requests.cookies import RequestsCookieJar

from plugins_v3._login import config
from utils.exceptions import custom_abort
from utils.redis_connections import redis_session
from utils.session import session

with open('plugins_v3/_login/rsa.js') as f:  # 执行 JS 文件
    js_ctx = execjs.compile(f.read())


def follow_link(cookies: RequestsCookieJar, url: str) -> (Response, RequestsCookieJar):
    while True:
        resp = session.get(url, cookies=cookies, allow_redirects=False)
        cookies.update(resp.cookies)
        if not resp.headers.get('location') or resp.headers.get('location').find('http') == -1:
            return resp, cookies
        else:
            url = resp.headers.get('location')


def login(name: str, passwd: str, disable_cache=False, all_cookies=True) -> RequestsCookieJar:
    if not name or not passwd:
        custom_abort(-3, '账号密码不能为空')
    if name.strip() != name:
        custom_abort(-3, '用户名包含空字符')
    if not disable_cache:
        cookie_pickle = redis_session.get("cookie" + name)
        if cookie_pickle:
            cookies = pickle.loads(cookie_pickle)
            r = session.get(config.test_url, allow_redirects=False, cookies=cookies)
            if r.status_code == 200:
                if all_cookies:
                    _, cookies = follow_link(cookies, "http://222.31.49.139/jwglxt/xtgl/index_initMenu.html")
                redis_session.set("cookie" + name, pickle.dumps(cookies), ex=43200)
                return cookies
            else:
                redis_session.delete("cookie" + name)
    index_response = session.get(config.index_url)
    cookies = index_response.cookies
    execution = re.search('name="execution" value="(.*?)"', index_response.content.decode()).group(1)
    public_key_dict_resp = session.get(config.public_key_url, cookies=cookies)
    cookies.update(public_key_dict_resp.cookies)
    public_key_dict = public_key_dict_resp.json()
    post_data = {
        'mobileCode': '',
        'authcode': '',
        '_eventId': 'submit',
        'execution': execution,
        'username': name,
        'password': js_ctx.call('fuck', public_key_dict["exponent"], public_key_dict["modulus"], passwd)
    }
    login_response = session.post(config.index_url, allow_redirects=False, data=post_data, cookies=cookies)
    # 跟随一些列 302 跳转，并更新 cookies
    cookies.update(login_response.cookies)
    if login_response.status_code == 302:
        login_response, cookies = follow_link(login_response.cookies, login_response.headers.get('location'))
    login_response_html = login_response.content.decode()
    if login_response_html.find("用户名或密码错误") != -1:
        custom_abort(-3, '账号或密码错误')
    elif login_response_html.find("完成，进入门户") != -1:
        custom_abort(-3, '未绑定手机号')
    if all_cookies:
        _, cookies = follow_link(cookies, "http://222.31.49.139/jwglxt/xtgl/index_initMenu.html")
    # print(pickle.dumps(cookies))
    redis_session.set("cookie" + name, pickle.dumps(cookies), ex=43200)
    return cookies
