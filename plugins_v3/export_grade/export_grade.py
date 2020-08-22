import hashlib
import os

from flask import request
from qiniu import Auth, put_file

from global_config import qiniu as qiniu_config, app_secret
from plugins_v3._login.login import login
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.decorators.stopped import stopped
from utils.exceptions import custom_abort
from . import api
from .config import *

q = Auth(qiniu_config['access_key'], qiniu_config['secret_key'])
bucket_name = 'blog_cdn'


def upload_to_qiniu(file_name):
    token = q.upload_token(bucket_name, file_name, 3600)
    put_file(token, file_name, file_name)
    os.remove(file_name)


@api.route('/exportGrade', methods=['GET'])
@check_sign(check_args={'name', 'passwd', 'type'})
@stopped()
@request_limit()
@need_proxy()
def handle_export_grade():
    name = request.args.get('name', type=str)
    passwd = request.args.get('passwd', type=str)
    file_type = request.args.get('type', 'pdf')
    session = login(name, passwd)
    if file_type == 'pdf':
        post_data1 = {
            'gsdygx': '10353-zw-mrgs1'
        }
        pdf_message = session.post(pdf_url1, data=post_data1).content.decode()
        if pdf_message.find('可打印') == -1:
            custom_abort(-3, pdf_message)
        pdf_url = session.post(pdf_url2, data=post_data1).content.decode().replace('\\', '').replace('\"',
                                                                                                     '')
        if pdf_url.find('成功') != -1:
            pdf_content = session.get('http://222.31.49.139' + pdf_url.split('#')[0]).content
            file_name = 'files/%s-grade-%s.pdf' % \
                        (name, hashlib.md5((name + app_secret).encode('utf-8')).hexdigest()[:5])
            with open(file_name, 'wb') as pdf_file:
                pdf_file.write(pdf_content)
            upload_to_qiniu(file_name)
            return {
                'code': 0,
                'data': {
                    'url': 'https://blog-cdn.dreace.top/' + file_name
                }
            }
        custom_abort(-3, pdf_url)
    else:
        xls_content = session.post(excel_url, data=post_data).content
        file_name = 'files/%s-grade-%s.xls' % \
                    (name, hashlib.md5((name + app_secret).encode('utf-8')).hexdigest()[:5])
        with open(file_name, 'wb') as xls_file:
            xls_file.write(xls_content)
        upload_to_qiniu(file_name)
        return {
            'code': 0,
            'message': {
                'url': 'https://blog-cdn.dreace.top/' + file_name
            }
        }
