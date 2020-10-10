from flask import Blueprint

api = Blueprint('exam_v3', __name__, url_prefix='/v3')

from .exam import *

