#! /usr/bin/env python
from flask import abort, jsonify, request, Blueprint
from . import db
from app.models import User

api = Blueprint('api', __name__, url_prefix='/api/v1')
authent = Blueprint('authent', __name__, url_prefix='/api/v1/auth')


@api.route("/", methods=["GET"])
def index():
    return "nothing to see here move along"


@authent.route("/register", methods=["POST"])
def register_user():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    if username is None or password is None or email is None:
        return jsonify({"message": "error in input"}), 400  # missing arguments
    if Users.query.filter_by(username=username).first() is not None:
        # existing user
        return jsonify({"message": "username already taken"}), 403
    if Users.query.filter_by(email=email).first() is not None:
        # existing email
        return jsonify({"message": "email already in use"}), 403
    user = Users(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "successfully registered user",
                    "username": user.username, "email": user.email}), 201


@authent.route('/login', methods=["POST"])
def return_token():
    # return jsonify({"token": "some string"})
    username = request.json.get("username")
    password = request.json.get("password")
    if username is None or password is None:
        return jsonify({"message": "wrong username password combination"}), 400 # missing arguments
    user =
    if Users.query.filter_by(username=username).first() is not None:
        pass
        # the username exists in the system go forward and check password
        # hash against the one stored in the db


@api.route('/bucketlists', methods=["GET", "POST"])
def dummy_func():
    return jsonify({"message": "something small"})
