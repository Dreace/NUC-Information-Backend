from flask import Blueprint

api = Blueprint('get_idle_classroom_api', __name__)

from .get_idle_classroom import *