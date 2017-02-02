#! /usr/bin/env python
from flask_restful import abort, Resource, reqparse, marshal_with
from flask import abort, jsonify, request
from . import db
from app.models import User, Bucketlist, Item
from app.authenticate import multi_auth, g
from app.format import itemformat, bucketlistformat


def save(target):
    """ utility function to simplify save operation to DB"""
    db.session.add(target)
    db.session.commit()


def delete(target):
    """ utility function to simplify delete operation to DB"""
    db.session.delete(target)
    db.session.commit()


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
        return {"message": msg}, 201


class BucketAction(Resource):
    decorators = [multi_auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(BucketAction, self).__init__()

    def post(self):
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="bucketlist name required")
        args = self.reqparse.parse_args()
        name = args.name
        bucket = Bucketlist(name=name, user_id=g.user.id)
        save(bucket)
        msg = ("bucketlist -" + bucket.name + "- has been successfully "
               "created with ID: " + str(bucket.id))
        return {"message": msg}, 201

    @marshal_with(bucketlistformat)
    def get(self, id=None):
        search = request.args.get("q") or None
        page = request.args.get("page") or 1
        limit = request.args.get("limit") or 20
        if id:
            bucketlist = Bucketlist.query.filter_by(id=id).first()
            if not bucketlist or (bucketlist.user_id != g.user.id):
                abort(404, "bucketlist not found")
            return bucketlist, 200

        if search:
            bucket_search = Bucketlist.query.filter(Bucketlist.name.ilike(
                "%" + search + "%")).filter_by(user_id=g.user.id).paginate(
                int(page), int(limit), False)
            if len(bucket_search.items) == 0:
                abort(404, "bucketlist of that name not found")
            else:
                bckt = [bckt for bckt in bucket_search.items]
                return bckt, 200

        bucketlists = Bucketlist.query.filter_by(user_id=g.user.id).all()
        return bucketlists, 200

    def put(self, id):
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="bucketlist name required")
        args = self.reqparse.parse_args()
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist or (bucketlist.user_id != g.user.id):
            abort(404, "bucketlist not found")
        bucketlist.name = args.name
        save(bucketlist)
        msg = ("bucketlist ID: " + str(bucketlist.id) + " has been updated")
        return {"message": msg}, 200

    def delete(self, id=None):
        if not id:
            abort(400, "bad request")
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist or (bucketlist.user_id != g.user.id):
            abort(404, "bucketlist not found")
        delete(bucketlist)
        msg = ("bucketlist : " + bucketlist.name + " has been deleted")
        return {"message": msg}, 200


class ItemAction(Resource):
    decorators = [multi_auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ItemAction, self).__init__()

    def post(self, id=None):
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="Item name required")
        args = self.reqparse.parse_args()
        if not id:
            abort(400, "bad request")
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist or (bucketlist.user_id != g.user.id):
            abort(404, "bucketlist not found, confirm the id")
        item = Item(name=args.name, bucket_id=id)
        save(item)
        msg = ("item has been added to the bucketlist")
        return {"message": msg}, 201

    def put(self, id=None, item_id=None):
        self.reqparse.add_argument("name", type=str, location="json",
                                   help="item name required")
        self.reqparse.add_argument("status", type=bool, location="json",
                                   help="item status required")
        args = self.reqparse.parse_args()
        if not id or not item_id:
            abort(400, "bad request")
        bucket = Bucketlist.query.filter_by(id=id).first()
        item = Item.query.filter_by(id=item_id).first()
        if not bucket or (bucket.user_id != g.user.id) or not item:
            abort(404, "item not found, confirm bucketlist and item id")
        if args["name"] is None and args["status"] is None:
            abort(400, "provide at least one parameter to change")
        if args["name"]:
            item.name = args["name"]
        if args["status"]:
            item.status = args["status"]

        return {"message": "item has been updated"}, 200

    def delete(self, id=None, item_id=None):
        if not id or not item_id:
            abort(400, "bad request")
        bucket = Bucketlist.query.filter_by(id=id).first()
        item = Item.query.filter_by(id=item_id).first()
        if not bucket or (bucket.user_id != g.user.id) or not item:
            abort(404, "item not found, confirm bucketlist and item id")
        delete(item)

        return {"message": "item has been deleted successfully"}, 200
