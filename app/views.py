#! /usr/bin/env python
from flask_restful import Resource, reqparse
from flask import abort, jsonify, request, Blueprint
from . import db
from app.models import User, Bucketlist
from app.authenticate import multi_auth, g
# import json_schema


def save(target):
    """ utility function to simplify save operation to DB"""
    db.session.add(target)
    db.session.commit()


api_rt = Blueprint("api", __name__, url_prefix="/api/v1")
authent = Blueprint("authent", __name__, url_prefix="/api/v1/auth")


@api_rt.route("/", methods=["GET"])
@multi_auth.login_required
def index_check():
    return "nothing to see here move along %s" % g.user.email


class LoginUser(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True,
                                   location='json', help="username required")
        self.reqparse.add_argument('password', type=str, required=True,
                                   location='json', help="password required")
        super(LoginUser, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username = args.username
        password = args.password

        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return {"message": "wrong login details"}, 401
        token = user.generate_confirmation_token()
        return {"token": token.decode("ascii")}, 200


class RegisterUser(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True,
                                   location="json", help="username required")
        self.reqparse.add_argument("password", type=str, required=True,
                                   location="json", help="password required")
        self.reqparse.add_argument("email", type=str, required=True,
                                   location="json", help="email required")
        super(RegisterUser, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username = args.username
        password = args.password
        email = args.email

        user_reg = User.query.filter_by(username=username).first()
        if user_reg is not None:
            return {"message": "username already taken"}, 401
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        msg = "user " + user.username + " has been successfully added"
        return {"message": msg}


class BucketGet(Resource):
    decorators = [multi_auth.login_required]

    def post(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="bucketlist name required")
        args = self.reqparse.parse_args()
        name = args.name
        bucket = Bucketlist(name=name, user_id=g.user.id)
        save(bucket)
        msg = ("bucketlist -" + bucket.name + "- has been successfully "
               "created with ID: " + str(bucket.id))
        return {"message": msg}

    def get(self):
        bckt_list = []
        items = []
        buckets = Bucketlist.query.filter_by(user_id=g.user.id).all()
        if not buckets:
            return bckt_list
        for bucket in buckets:
            bucket_dict = {"id": bucket.id,
                           "name": bucket.name,
                           "items": items,
                           "date_created": bucket.date_created.strftime("%B %d, %Y"),
                           "date_modified": str(bucket.date_modified),
                           "created_by": g.user.username}
            bckt_list.append(bucket_dict)
        return bckt_list




@authent.route("/register", methods=["POST"])
def register_user():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    if username is None or password is None or email is None:
        return jsonify({"message": "error in input"}), 400  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        # existing user
        return jsonify({"message": "username already taken"}), 403
    if User.query.filter_by(email=email).first() is not None:
        # existing email
        return jsonify({"message": "email already in use"}), 403
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "successfully registered user",
                    "username": user.username, "email": user.email}), 201


@authent.route('/login', methods=["POST"])
def return_token():
    username = request.json.get("username")
    password = request.json.get("password")
    user = User.query.filter_by(username=username).first()
    if username is None or password is None or user is None:
        return jsonify({"message": "wrong username password combination"}), 400 # missing arguments
    if not user.verify_password(password):
        return jsonify({"message": "wrong login details"}), 401
    token = user.generate_confirmation_token()
    return jsonify({"token": token.decode("ascii")}), 200


@api_rt.route('/bucketlists', methods=["GET", "POST"])
def dummy_func():
    return jsonify({"message": "something small"})
