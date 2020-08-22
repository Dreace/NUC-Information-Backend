from flask import Blueprint

api = Blueprint('export_grade_v3', __name__, url_prefix='/v3')

from .export_grade import *
