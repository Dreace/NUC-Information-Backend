from flask import Blueprint

api = Blueprint('test_v3', __name__, url_prefix='/v3')

from .test_url import *
