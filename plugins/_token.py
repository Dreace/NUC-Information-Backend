from flask import Blueprint
from flask import request
from flask import Response
from flask import current_app
from redis_connect import redis_token
import hashlib
import base64
import random
import string
import json

api = Blueprint('get_token_api', __name__)


@api.route('/Token', methods=['GET'])
def get_token():
    key = request.args.get('key', "")
    sign = request.args.get('sign', "")
    res = generate_token(key, sign)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def generate_token(key, sign):
    message = "OK"
    error = ""
    code = 0
    data = ""
    if hashlib.md5(base64.b64encode(key.encode("utf-8"))).hexdigest() != sign:
        message = "鉴权失败"
        error = "非法 Key"
        code = -1
    else:
        key += ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        token = hashlib.md5(base64.b64encode(key.encode("utf-8"))).hexdigest()
        redis_token.set(token, token, ex=3600)
        data = {
            "token": token
        }
    return {"message": message, "error": error, "code": code, "data": data}
