
from flask import Flask

from .config import Config
from .auth import auth

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['zip'] = zip
    app.config.from_object(Config)
    app.register_blueprint(auth)
    # app.config['SECRET_KEY'] = 'SUPER SECRETO'

    return app