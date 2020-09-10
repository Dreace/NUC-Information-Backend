from flask import Blueprint

api = Blueprint('empty_classroom_v3', __name__, url_prefix='/v3')

from .empty_classroom import *

