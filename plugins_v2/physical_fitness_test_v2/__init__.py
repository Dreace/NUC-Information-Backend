from flask import Blueprint

api = Blueprint('fitness_api_v2', __name__, url_prefix="/v2/fitness")

from .physical_fitness_test_v2 import *
