#! /usr/bin/env python
from flask_restful import abort, inputs, Resource, reqparse, marshal_with
from flask import abort, jsonify, request
from app import db, expiry_time
from app.models import User, Bucketlist, Item
from app.authenticate import multi_auth, g
from app.validate_format import (itemformat, bucketlistformat, validate_string,
                                 save, delete, is_not_empty)


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
        token = user.generate_confirmation_token(expiry_time)
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
        username, password, email = (args["username"], args["password"],
                                     args["email"])

        if not validate_string(username):
            return {"message": ("only numbers, letters, '-','_' allowed"
                                " in username")}, 400
        if not is_not_empty(username, password, email):
            return {"message": "no blank fields allowed"}, 400
        # validate the email field
        if not ("@" in email):
            return {"message": "email is invalid"}, 400
        user_reg = User.query.filter_by(username=username).first()
        if user_reg is not None:
            return {"message": "username already taken"}, 403
        user = User(username=username, email=email, password=password)
        save(user)
        msg = "user " + user.username + " has been successfully added"
        return {"message": msg}, 201


class BucketAction(Resource):
    decorators = [multi_auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(BucketAction, self).__init__()

    def post(self, id=None):
        if id:
            abort(400, "bad request")
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="bucketlist name required")
        args = self.reqparse.parse_args()
        name = args.name
        if not is_not_empty(name):
            return {"message": "no blank fields allowed"}, 400
        if name.isspace():
            return {"message": "name is invalid"}, 400
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

        if page or limit:
            bucket_collection = Bucketlist.query.filter_by(
                user_id=g.user.id).paginate(int(page), int(limit), False)
            bucket_disp = [bckt for bckt in bucket_collection.items]
            return bucket_disp, 200

        bucketlists = Bucketlist.query.filter_by(user_id=g.user.id).all()
        return bucketlists, 200

    def put(self, id):
        self.reqparse.add_argument("name", type=str, required=True,
                                   location="json",
                                   help="bucketlist name required")
        args = self.reqparse.parse_args()
        name = args["name"]
        if not is_not_empty(name):
            return {"message": "no blank fields allowed"}, 400
        if name.isspace():
            return {"message": "name is invalid"}, 400
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist or (bucketlist.user_id != g.user.id):
            abort(404, "bucketlist not found")
        bucketlist.name = name
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
        name = args["name"]
        if not is_not_empty(name):
            return {"message": "no blank fields allowed"}, 400
        if name.isspace():
            return {"message": "name is invalid"}, 400
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist or (bucketlist.user_id != g.user.id):
            abort(404, "bucketlist not found, confirm the id")
        item = Item(name=name, bucket_id=id)
        save(item)
        msg = ("item has been added to the bucketlist")
        return {"message": msg}, 201

    def put(self, id=None, item_id=None):
        self.reqparse.add_argument("name", type=str, location="json",
                                   help="item name required")
        self.reqparse.add_argument("status", type=inputs.boolean,
                                   location="json",
                                   help="status required as true or false")
        args = self.reqparse.parse_args()
        name = args["name"]
        status = args["status"]
        if not id or not item_id:
            abort(400, "bad request")
        if name is None and status is None:
            abort(400, "provide at least one parameter to change")

        bucket = Bucketlist.query.filter_by(id=id).first()
        item = Item.query.filter_by(id=item_id).first()
        if not bucket or (bucket.user_id != g.user.id) or not item:
            abort(404, "item not found, confirm bucketlist and item id")
        if not is_not_empty(name):
            return {"message": "name can't be blank"}, 400
        if name:
            if name.isspace():
                return {"message": "name is invalid"}, 400
            item.name = name
        if status:
            item.status = status

        return {"message": "item has been updated"}, 200

    def delete(self, id=None, item_id=None):
        bucket = Bucketlist.query.filter_by(id=id).first()
        item = Item.query.filter_by(id=item_id).first()
        if not bucket or (bucket.user_id != g.user.id) or not item:
            abort(404, "item not found, confirm bucketlist and item id")
        delete(item)

        return {"message": "item has been deleted successfully"}, 200
