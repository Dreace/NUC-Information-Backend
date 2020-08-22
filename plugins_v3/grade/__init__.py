from flask import Blueprint

api = Blueprint('grade_v3', __name__, url_prefix='/v3')

from .grade import *
