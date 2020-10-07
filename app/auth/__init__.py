from flask import Blueprint

aleph = Blueprint('aleph', __name__, url_prefix='/aleph')

from . import views