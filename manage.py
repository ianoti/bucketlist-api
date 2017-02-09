#!/usr/bin/env python

import os
from app import create_app, db, api
from app.models import User, Bucketlist, Item
from app.views import LoginUser, RegisterUser, BucketAction, ItemAction

from flask_script import Manager, Shell, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from flask import jsonify


# make Flask application from app factory
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# initialise manager class
manager = Manager(app)
# initialise migrate class
migrate = Migrate(app, db)


# make custom error json codes
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, message=str(e)), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify(error=500, message=str(e)), 500


def make_shell_context():
    """ this imports the modules into shell to reduce tediousness """
    return dict(app=app, db=db, User=User, Bucketlist=Bucketlist,
                Items=Item)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def initdb():
    """ initialise the database with creation of tables """
    db.create_all()
    print("database has been initialised")


@manager.command
def dropdb():
    """ delete all the data in the database and destroy all the tables """
    if prompt_bool("Are you sure you want to destroy all your data"):
        db.drop_all()
        print("the data in the database has been destroyed and tables removed")


if __name__ == "__main__":
    api.add_resource(LoginUser, "/auth/login", endpoint="token")
    api.add_resource(RegisterUser, "/auth/register", endpoint="register")
    api.add_resource(BucketAction, "/bucketlists", "/bucketlists/<id>",
                     endpoint="bucketlist")
    api.add_resource(ItemAction, "/bucketlists/<id>/items",
                     "/bucketlists/<id>/items/<item_id>",
                     endpoint="items")
    manager.run()
