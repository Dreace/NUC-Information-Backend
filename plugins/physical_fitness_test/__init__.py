from flask import Blueprint

api = Blueprint('physical_fitness_test_api', __name__)

from .physical_fitness_test import *
