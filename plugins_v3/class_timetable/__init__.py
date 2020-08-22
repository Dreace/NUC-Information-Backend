from flask import Blueprint

api = Blueprint('class_timetable_v3', __name__, url_prefix='/v3')

from .class_timetable import *
