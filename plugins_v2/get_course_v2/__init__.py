from flask import Blueprint

# api = Blueprint('get_course_api_v2', __name__, url_prefix="/v2")
# TODO 兼容现有版本
api = Blueprint('get_course_api_v2', __name__)

from .get_course_v2 import *
