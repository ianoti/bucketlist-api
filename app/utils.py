import string
from app import db


def validate_string(string_passed):
    """ ensure username only has letters, numbers, _ and -
    return true if the username has valid characters"""
    letters = string.ascii_letters
    numbers = string.digits
    allowed = letters + numbers + "-" + "_"
    return all(char in allowed for char in string_passed)


def save(target):
    """ utility function to simplify save operation to DB"""
    db.session.add(target)
    db.session.commit()


def delete(target):
    """ utility function to simplify delete operation to DB"""
    db.session.delete(target)
    db.session.commit()


def is_not_empty(*args):
    """ check that the arguments passed are not empty and return true"""
    return all(len(value) > 0 for value in args)
