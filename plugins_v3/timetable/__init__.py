from flask import Blueprint

api = Blueprint('timetable_v3', __name__, url_prefix='/v3')

from .timetable import *
from .export import *
