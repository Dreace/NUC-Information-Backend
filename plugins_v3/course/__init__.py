from flask import Blueprint

api = Blueprint('course_v3', __name__, url_prefix='/v3')

from .course import *
