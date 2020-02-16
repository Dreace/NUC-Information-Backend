from flask import Blueprint

api = Blueprint('login_PhyEws_api', __name__)

from .login_PhyEws import *