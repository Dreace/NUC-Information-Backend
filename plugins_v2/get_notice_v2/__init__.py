from flask import Blueprint

api = Blueprint('get_notice_v2', __name__, url_prefix="/v2/notice")

from .get_notice_v2 import *