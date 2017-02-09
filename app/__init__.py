from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import configset, expiry_time

# use the blueprint to make url accessible between application and test
api_blue_print = Blueprint("api", __name__, url_prefix="/api/v1")
# initialise the Api class
api = Api(api_blue_print)
# initialise SQLAlchemy class
db = SQLAlchemy()


def create_app(config_set):
    """
    This initialises the app and sets the settings specified in the
    config file
    """
    app = Flask(__name__)
    app.config.from_object(configset[config_set])
    configset[config_set].init_app(app)

    db.init_app(app)
    app.register_blueprint(api_blue_print)

    return app
