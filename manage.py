#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Bucketlist, Item
from app.views import LoginUser, RegisterUser, BucketAction, ItemAction

from flask_script import Manager, Shell, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api


# make Flask application from app factory
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# initialise manager class
manager = Manager(app)
# initialise migrate class
migrate = Migrate(app, db)
api = Api(app=app)


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
    # print(api.__dir__)
    api.add_resource(LoginUser, "/api/v2/auth/login", endpoint="token")
    api.add_resource(RegisterUser, "/api/v2/auth/register",
                     endpoint="register")
    api.add_resource(BucketAction, "/api/v2/bucketlists",
                     "/api/v2/bucketlists/<id>", endpoint="bucketlist")
    api.add_resource(ItemAction, "/api/v2/bucketlists/<id>/items",
                     "/api/v2/bucketlists/<id>/items/<item_id>",
                     endpoint="items")
    manager.run()
