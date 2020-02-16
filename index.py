import gevent.monkey

gevent.monkey.patch_all()
import time

from global_config import no_limit_url, guest_data, request_limit_max, appSecret, dont_cache_url, request_limit
import load_task
from scheduler import scheduler
import plugin
from pywsgi import WSGIServer
from os import path
from flask import Flask, redirect
from flask import request
from flask import Response
import hashlib
# from werkzeug.contrib.fixers import ProxyFix
import traceback
import flask_compress
from urllib.parse import unquote, quote
import json
from redis_connect import redis_request_limit, redis_cache
from logger import root_logger
import logging

app = Flask(__name__)
flask_compress.Compress(app)


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("由于 404 重定向 %s", request.url)
    return redirect('https://dreace.top')


@app.errorhandler(Exception)
def on_sever_error(e):
    global request_limit
    traceback.print_exc()
    message = "服务器错误"
    error = "未知错误"
    code = -1
    data = ""
    resp = Response(json.dumps({"message": message, "error": error, "code": code, "data": data}),
                    mimetype='application/json')
    return resp


request_limit = request_limit


# @app.before_request
def check_auth():
    global request_limit
    request_limit += 1
    message = "OK"
    error = ""
    code = 0
    data = ""
    name = request.args.get('name', "")
    args = dict(request.args)
    if request.url.find("MessagePush") == -1:
        if not check_sign(args):
            logging.warning("身份认证失败")
            message = "身份认证失败"
            error = "身份认证失败"
            code = -2
        if "ts" not in args.keys() or int(args["ts"]) + 3e5 < int(time.time() * 1000):
            logging.warning("拒绝本次请求")
            message = "拒绝本次请求"
            error = "拒绝本次请求"
            code = -3
        # if name and time.localtime(time.time())[3] < 7:
        #     logging.warning("非服务时间", )
        #     message = "非服务时间"
        #     error = "非服务时间"
        #     code = -1
        elif request.path[1:] not in no_limit_url and not check_request_limit(request.args["key"]):
            logging.warning("拒绝了 %s 的请求", request.args["key"])
            message = "操作过频繁"
            error = "操作过频繁"
            code = -1
        if name == "guest" and request.path[1:] in guest_data.keys():
            data = guest_data[request.path[1:]]
        if code != 0 or len(data) > 1:
            resp = Response(json.dumps({"message": message, "error": error, "code": code, "data": data}),
                            mimetype='application/json')
            return resp
        url = request.path + "?" + get_cache_key(dict(request.args))
        url_md5 = hashlib.md5(url.encode()).hexdigest()
        res_b = redis_cache.get(url_md5)
        if res_b:
            res = json.loads(res_b)
            res["cached"] = 1
            resp = Response(json.dumps(res), mimetype='application/json')
            logging.info("命中缓存 %s", unquote(url))
            return resp
        if request_limit >= request_limit_max:
            logging.warning("服务器繁忙")
            message = "服务器繁忙"
            code = -1
            resp = Response(json.dumps({"message": message, "error": error, "code": code, "data": data}),
                            mimetype='application/json')
            return resp


def get_cache_key(args: dict):
    if "sign" in args.keys():
        del args["sign"]
    if "ts" in args.keys():
        del args["ts"]
    args_list = []
    for k in sorted(args):
        args_list.append(k + "=" + args[k])
    return "&".join(args_list)


def check_sign(args: dict):
    if "sign" not in args.keys():
        return False
    sign = args["sign"]
    del args["sign"]
    args_list = []
    for k in sorted(args):
        args_list.append(k + "=" + quote(args[k], safe="~()*!.\'"))
    arg = "&".join(args_list)
    return sign == hashlib.md5((arg + appSecret).encode("utf-8")).hexdigest()


@app.after_request
def cache_request(response):
    global request_limit
    request_limit -= 1
    try:
        res = json.loads(response.get_data())
        if "cached" not in res.keys() and res["code"] == 0 and request.path[1:] not in dont_cache_url:
            url = request.path + "?" + get_cache_key(dict(request.args))
            redis_cache.set(hashlib.md5(url.encode()).hexdigest(), json.dumps(res), 5400)
            logging.info("缓存 %s", unquote(url))
    except:
        pass
    return response


def check_request_limit(user_key):
    if redis_request_limit.llen(user_key) < 30:
        redis_request_limit.lpush(user_key, time.time())
    else:
        first_time = redis_request_limit.lindex(user_key, -1)
        if time.time() - float(first_time) < 300:
            return False
        else:
            redis_request_limit.lpush(user_key, time.time())
            redis_request_limit.ltrim(user_key, 0, 29)
    redis_request_limit.expire(user_key, 3600)
    return True


def initializer(context=None):
    plugins = plugin.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'plugins'
    )
    plugins.union(plugin.load_plugins(
        path.join(path.dirname(__file__), 'plugins_v2'),
        'plugins_v2'
    ))
    for i in plugins:
        app.register_blueprint(i.api)

    load_task.load_tasks(
        path.join(path.dirname(__file__), 'tasks'),
        'tasks')
    scheduler.start()
    # print(app.url_map)


if __name__ == '__main__':
    initializer()
    http_server = WSGIServer(('0.0.0.0', 100), app, log=root_logger, error_log=root_logger)
    http_server.serve_forever()


def handler(environ, start_response):
    return app(environ, start_response)
