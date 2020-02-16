from flask import Blueprint

api = Blueprint('get_grade_api_v2', __name__, url_prefix="/v2")

from .get_grade_v2 import *
