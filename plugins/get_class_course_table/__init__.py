from flask import Blueprint

api = Blueprint('get_class_course_table_api', __name__)

from .get_class_course_table import *