from flask import Blueprint

api = Blueprint('get_grade_2_api', __name__)

from .get_grade_2 import *