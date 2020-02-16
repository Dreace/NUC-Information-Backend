from flask import Blueprint

api = Blueprint('get_course_table_api_v2', __name__, url_prefix="/v2")

from .get_course_table_v2 import *
