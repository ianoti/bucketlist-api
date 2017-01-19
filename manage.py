from flask_script import Manager
# import commands
from app.bucketlist import app
# import config

manager = Manager(app)


if __name__ == "__main__":
    # manager.add_option("-c", "--config", dest="config", required=False,
    #                    default=config.Dev)
    # manager.add_command("test", commands.Test())
    manager.run()
    manager.run()
