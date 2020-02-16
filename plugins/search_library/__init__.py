from flask import Blueprint

api = Blueprint('search_library_api', __name__)

from .search_library import *
