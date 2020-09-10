from flask import Blueprint

api = Blueprint('news_v3', __name__, url_prefix='/v3')

from .news import *
