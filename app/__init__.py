from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import configset
# make the api blueprint to make routes accessible

# initialise SQLAlchemy class
db = SQLAlchemy()

# initialise the Api class
# api = Api()


def create_app(config_set):
    """
    This initialises the app and sets the settings specified in the
    config file
    """
    app = Flask(__name__)
    app.config.from_object(configset[config_set])
    configset[config_set].init_app(app)

    db.init_app(app)
    from app.views import api_rt, authent
    app.register_blueprint(api_rt)
    app.register_blueprint(authent)
    # api = Api(app)

    return app
