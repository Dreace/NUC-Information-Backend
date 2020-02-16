from flask import Blueprint

api = Blueprint('get_grade_api', __name__)

from .get_grade import *