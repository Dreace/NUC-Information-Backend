from flask import Blueprint

api = Blueprint('library_api_v3', __name__, url_prefix='/v3')

from .library import *
