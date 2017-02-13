import string
from app import db


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
