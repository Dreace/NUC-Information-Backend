from flask import Blueprint

api = Blueprint('export_grade_api_v2', __name__, url_prefix="/v2")

from .export_grade_v2 import *
