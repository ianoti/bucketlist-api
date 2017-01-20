#! /usr/bin/env python
from flask import Blueprint
from . import db

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.route('/', methods=["GET"])
def index():
    return "nothing to see here move along"
