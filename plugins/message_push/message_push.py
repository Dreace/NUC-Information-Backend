import json
import logging
import traceback

import requests
from flask import Response
from flask import request

from . import api


@api.route('/MessagePush', methods=['POST'])
def handle_message_push():
    data = request.json
    res = message_push(data)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def message_push(data):
    title = "小程序反馈更新了"
    message = "但不知发生了什么"
    try:
        if "type" in data.keys():
            if data["type"] == "post.created":
                title = "%s%s发表了一个主贴" % (data["payload"]["post"]["nick_name"], data["payload"]["post"]["time"])
                message = data["payload"]["post"]["content"]
            elif data["type"] == "post.updated":
                title = "%s%s发表的主贴已更新" % (data["payload"]["post"]["nick_name"], data["payload"]["post"]["time"])
                message = data["payload"]["post"]["content"]
            elif data["type"] == "reply.created":
                title = "%s%s发表了一个回复" % (data["payload"]["reply"]["nick_name"], data["payload"]["reply"]["time"])
                message = data["payload"]["reply"]["content"]
            elif data["type"] == "reply.updated":
                title = "%s%s发表的回复已更新" % (data["payload"]["reply"]["nick_name"], data["payload"]["reply"]["time"])
                message = data["payload"]["reply"]["content"]
        logging.info("反馈标题：%s" % title)
        logging.info("反馈内容：%s" % message)
        requests.post(
            "https://api2.day.app:4443/ReNCULrNA3AxYFopZyKipB/%s/%s" % (
            title.replace("/", "%2f"), message.replace("/", "%2f")))
        logging.info("反馈信息推送成功")
    except:
        logging.error(traceback.format_exc())
        logging.error("反馈信息推送失败")
    return {}
