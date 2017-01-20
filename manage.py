#!/usr/bin/env python

import os
from app import create_app, db
from app.models import Users, Bucketlists, Items
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


# make Flask application from app factory
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# initialise manager class
manager = Manager(app)
# initialise migrate class
migrate = Migrate(app, db)


def make_shell_context():
    """ this imports the modules into shell to reduce tediousness """
    return dict(app=app, db=db, Users=Users, Bucketlists=Bucketlists,
                Items=Items)
    
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()
