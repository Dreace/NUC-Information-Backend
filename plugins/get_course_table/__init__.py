from flask import Blueprint

api = Blueprint('get_course_table_api', __name__)

from .get_course_table import *