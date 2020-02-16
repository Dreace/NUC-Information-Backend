import pickle
import re

import requests

from redis_connect import redis_session
from .IVC import *
from .config import *


def auto_v_code(pic):
    return identificationVerificationCode(pic)


def login(name, passwd, disable_cache=False):
    if not disable_cache:
        if redis_session.exists("session" + name) == 1:
            session = pickle.loads(redis_session.get("session" + name).encode('latin1'))
            r = session.get(credit_url)
            if r.content.decode("gbk").find(u"学分") != -1:
                redis_session.set("session" + name, pickle.dumps(session).decode('latin1'), ex=3600)
                return session
            else:
                redis_session.delete("session" + name)
    session = requests.session()
    session.proxies = proxies
    session.headers = headers
    exit_flag = 1
    i = 0
    fuck_url = None
    while exit_flag:
        r = session.get(caurl)
        reg = r'<input type="hidden" name="lt" value="(.*)" />'
        pattern = re.compile(reg)
        result = pattern.findall(r.content.decode("gbk"))
        token = result[0]
        pic = session.get(vcodeurl).content
        v_code = auto_v_code(pic)
        postdata["username"] = name
        postdata["password"] = passwd
        postdata["j_captcha_response"] = v_code
        postdata["lt"] = token
        r = session.post(caurl, data=postdata)
        fuck_url = r.url
        if r.content.decode("gbk").find(u"用户名或密码错误") != -1:
            return 2
        if re.search(r'ticket', r.url):
            exit_flag = 0
        if i >= 10:
            return 1
        i += 1
    headers2["referer"] = r.url
    r = session.post(dwr_url, headers=headers2, data=postdata2)
    reg = r'\?yhlx=student\&login=(\d+)\&url=zf_loginAction\.do'
    pattern = re.compile(reg)
    result = pattern.findall(r.content.decode("gbk"))
    session.post("http://i.nuc.edu.cn/dwr/call/plaincall/portalAjax.insertYYDJJLB.dwr", headers=headers3,
                 data=postdata2)
    headers4["Referer"] = fuck_url
    session.get("https://ca.nuc.edu.cn/zfca/login?yhlx=student&login=" + result[0] + "&url=zf_loginAction.do",
                headers=headers4, data=postdata2)
    redis_session.set("session" + name, pickle.dumps(session).decode('latin1'), ex=3600)
    return session
