from flask_testing import TestCase
import json

from app import create_app, db, api
from app.views import LoginUser, RegisterUser, BucketAction, ItemAction
from app.models import User, Bucketlist, Item


class BaseTestClass(TestCase):
    """ the base test configuration """

    def create_app(self):
        app = create_app("testing")

        return app

    def setUp(self):
        self.app = self.create_app().test_client()
        db.create_all()
        self.mime_type = "application/json"
        # add resources to enable the testing environment to locate the routes
        api.add_resource(LoginUser, "/auth/login", endpoint="token")
        api.add_resource(RegisterUser, "/auth/register",
                         endpoint="register")
        api.add_resource(BucketAction, "/bucketlists",
                         "/bucketlists/<id>", endpoint="bucketlist")
        api.add_resource(ItemAction, "/bucketlists/<id>/items",
                         "/bucketlists/<id>/items/<item_id>",
                         endpoint="items")
        # Register users for tests
        details = json.dumps({"username": "johndoe", "password": "foobar",
                              "email": "john@example.com"})
        self.app.post("api/v1/auth/register", data=details,
                      content_type=self.mime_type)
        reg = json.dumps({"username": "janedoe", "password": "foobar",
                          "email": "jane@example.com"})
        self.app.post("api/v1/auth/register", data=reg,
                      content_type=self.mime_type)

        # user authenticated for test cases johndoe
        resp = self.app.post("/api/v1/auth/login", data=details,
                             content_type=self.mime_type)
        respdata = json.loads(resp.data)
        self.token = "Bearer " + respdata["token"]
        self.header = {"Authorization": self.token}

        # make dummy bucketlists
        bname = json.dumps({"name": "testlist"})
        self.app.post("/api/v1/bucketlists", data=bname, headers=self.header,
                      content_type=self.mime_type)
        # make dummy item
        iname = json.dumps({"name": "testlist"})
        self.app.post("/api/v1/bucketlists/1/items", data=iname,
                      headers=self.header, content_type=self.mime_type)

    def tearDown(self):
        """destroy all database contents """
        db.session.remove()
        db.drop_all()
