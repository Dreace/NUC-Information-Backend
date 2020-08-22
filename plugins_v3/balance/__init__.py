from flask import Blueprint

api = Blueprint('balance_v3', __name__, url_prefix='/v3')

from .balance import *
