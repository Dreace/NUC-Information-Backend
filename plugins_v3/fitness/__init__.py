from flask import Blueprint

api = Blueprint('fitness_v3', __name__, url_prefix='/v3')

from .fitness import *
