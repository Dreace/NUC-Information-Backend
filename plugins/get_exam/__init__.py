from flask import Blueprint

api = Blueprint('get_exam_api', __name__)

from .get_exam import *