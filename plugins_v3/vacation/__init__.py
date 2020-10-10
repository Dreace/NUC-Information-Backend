from flask import Blueprint

api = Blueprint('vacation_v3', __name__, url_prefix='/v3')

from .vacation import *
