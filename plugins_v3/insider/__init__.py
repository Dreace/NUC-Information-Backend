from flask import Blueprint

api = Blueprint('insider_v3', __name__, url_prefix='/v3')

from .insider import *
