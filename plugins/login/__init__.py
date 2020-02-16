from flask import Blueprint

api = Blueprint('login_api', __name__)

from .login import *
