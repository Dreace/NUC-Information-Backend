from flask import Blueprint

api = Blueprint('notice_v3', __name__, url_prefix='/v3')

from .notice import *