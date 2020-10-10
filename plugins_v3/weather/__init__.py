from flask import Blueprint

api = Blueprint('weather_v3', __name__, url_prefix='/v3')

from .weather import *
