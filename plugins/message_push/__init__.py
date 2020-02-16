from flask import Blueprint

api = Blueprint('message_push_api', __name__)

from .message_push import *