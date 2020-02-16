from flask import Blueprint

api = Blueprint('get_PhyEws_grade_api', __name__)

from .get_PhyEws_grade import *
