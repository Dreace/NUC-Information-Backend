from flask import Blueprint

# TODO 兼容现存客户端，客户端更新后可取消注释
# api = Blueprint('get_course_table_api_v2', __name__, url_prefix="/v2")
api = Blueprint('get_class_course_table_api', __name__)

from .get_class_course_table_v2 import *
