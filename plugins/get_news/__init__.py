from flask import Blueprint

api = Blueprint('get_news_api', __name__)

from .get_news import *