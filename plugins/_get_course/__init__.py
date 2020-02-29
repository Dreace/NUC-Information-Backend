from flask import Blueprint

api = Blueprint('get_course_api', __name__)

from .get_course import *