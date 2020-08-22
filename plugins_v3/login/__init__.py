from flask import Blueprint

api = Blueprint('login_v3', __name__, url_prefix='/v3')

from .login import *
