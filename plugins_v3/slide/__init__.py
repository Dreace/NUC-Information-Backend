from flask import Blueprint

api = Blueprint('slide_v3', __name__, url_prefix='/v3')

from .slide import *
