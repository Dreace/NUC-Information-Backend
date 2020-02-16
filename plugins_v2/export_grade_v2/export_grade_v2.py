import json
import os

from flask import Response
from flask import request
from qiniu import Auth, put_file

from plugins_v2._login_v2.login_v2 import login
from . import api
from .config import *

q = Auth(qiniu_access_key, qiniu_secret_key)
bucket_name = 'blog_cdn'


@api.route('/ExportGrade', methods=['GET'])
def handle_get_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    file_type = request.args.get('type', "pdf")
    res = get_grade(name, passwd, file_type)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def upload_to_qiniu(file_name):
    token = q.upload_token(bucket_name, file_name, 3600)
    put_file(token, file_name, file_name)
    os.remove(file_name)


def get_grade(name, passwd, file_type):
    message = "OK"
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, str):
            code = -1
            message = session
        else:
            if file_type == "pdf":
                post_data1 = {
                    "gsdygx": "10353-zw-mrgs1"
                }
                pdf_message = session.post(pdf_url1, data=post_data1).content.decode()
                if pdf_message.find("可打印") == -1:
                    code = -1
                    message = pdf_message
                else:
                    pdf_url = session.post(pdf_url2, data=post_data1).content.decode().replace("\\", "").replace("\"",
                                                                                                                 "")
                    if pdf_url.find("成功") != -1:
                        pdf_content = session.get("http://222.31.49.139" + pdf_url.split("#")[0]).content
                        file_name = "files/%s-grade.pdf" % name
                        with open(file_name, "wb") as pdf_file:
                            pdf_file.write(pdf_content)
                        upload_to_qiniu(file_name)
                        data = {
                            "url": "https://blog-cdn.dreace.top/" + file_name
                        }
                    else:
                        code = -1
                        message = pdf_url
            else:
                xls_content = session.post(excel_url, data=post_data).content
                file_name = "files/%s-grade.xls" % name
                with open(file_name, "wb") as xls_file:
                    xls_file.write(xls_content)
                upload_to_qiniu(file_name)
                data = {
                    "url": "https://blog-cdn.dreace.top/" + file_name
                }
    return {"message": message, "code": code, "data": data}
