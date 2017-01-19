from os import path

basedir = path.abspath(path.dirname(__file__))  # the path to the directory


class Config(object):
    """
    This class holds the base configurations for the project.
    It allows for the setup of the development environment
    and the testing environment
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'the_checkpoint_is_hot'


class Dev(Config):
    """
    This class holds the configuration for the development environment
    """
    DEVELOPMENT = True
    DEBUG = True


class Test(Config):
    """
    This class holds the configuration for the testing environment
    """
    TESTING = True
