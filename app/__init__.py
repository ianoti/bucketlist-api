from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import configset

# make the api blueprint to make routes accessible

# initialise SQLAlchemy class
db = SQLAlchemy()
# initialise the Api class


def create_app(config_set):
    """
    This initialises the app and sets the settings specified in the
    config file
    """
    app = Flask(__name__)
    app.config.from_object(configset[config_set])
    configset[config_set].init_app(app)

    db.init_app(app)

    from app.views import api, authent
    app.register_blueprint(api)
    app.register_blueprint(authent)

    return app
