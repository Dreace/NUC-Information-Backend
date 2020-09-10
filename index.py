import gevent.monkey

from models.sqlalchemy_db import db

gevent.monkey.patch_all()
import logging
import traceback
from os import path

import flask_compress
from flask import Flask, redirect, request

from pywsgi import WSGIServer
from startup import load_task, load_plugin
from utils.gol import global_values
from utils.logger import root_logger
from utils.scheduler import scheduler
from utils.exceptions import CustomHTTPException

from global_config import mysql as mysql_config

app = Flask(__name__)
flask_compress.Compress(app)

app.config['SQLALCHEMY_BINDS'] = {
    'nuc_info': 'mysql+pymysql://{}:{}@{}:3306/nuc_info'.format(mysql_config['user'], mysql_config['password'],
                                                                mysql_config['host'])
}

db.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("由于 404 重定向 %s", request.url)
    return redirect('https://dreace.top')


@app.errorhandler(CustomHTTPException)
def on_custom_http_exception(e: CustomHTTPException):
    return {
        'code': e.code,
        'message': e.message
    }


@app.errorhandler(Exception)
def on_sever_error(e):
    logging.exception(traceback.format_exc())
    return {
        'code': -1,
        'message': '服务器错误'
    }


def initializer():
    global_values.set_value("proxy_status_ok", True)
    plugins = load_plugin.load_plugins(
        path.join(path.dirname(__file__), 'plugins_v3'),
        'plugins_v3'
    )
    for i in plugins:
        app.register_blueprint(i.api)
    load_task.load_tasks(
        path.join(path.dirname(__file__), 'tasks'),
        'tasks')
    scheduler.start()


if __name__ == '__main__':
    initializer()
    # run_simple('0.0.0.0', 10001, app,
    #            use_reloader=True, use_debugger=True, use_evalex=True)
    http_server = WSGIServer(('0.0.0.0', 10050), app, log=root_logger, error_log=root_logger)
    http_server.serve_forever()
