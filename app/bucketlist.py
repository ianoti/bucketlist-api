#! /usr/bin/env python
from flask import Blueprint
from flask_restful import Resource
from . import db

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.route('/', methods=["GET"])
def index():
    return "nothing to see here move along"
