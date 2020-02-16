from flask import Blueprint

api = Blueprint('login_api_v2', __name__, url_prefix="/v2")

from .login_v2 import *
