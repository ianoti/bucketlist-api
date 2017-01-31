import unittest
import json
from app import create_app, db
from app.models import Users


class BucketlistUserRegisterTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.mime_type = "application/json"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        data = json.dumps({"username": "johndoe", "password": "johndoe",
                           "email": "johndoe@example.com"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data, content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual("successfully registered user",
                         server_resp["message"])

    def test_register_existing_username(self):
        user = Users(username="johndoe", email="john@example.com",
                     password="foobar")
        db.session.add(user)
        db.session.commit()
        data = json.dumps({"username": "johndoe", "password": "foo",
                           "email": "john@example.com"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data, content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual("username already taken",
                         server_resp["message"])

    def test_register_existing_email(self):
        user = Users(username="johndoe", email="john@example.com",
                     password="foobar")
        db.session.add(user)
        db.session.commit()
        data = json.dumps({"username": "johnguy", "password": "foo",
                           "email": "john@example.com"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data, content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual("email already in use",
                         server_resp["message"])

    def test_register_missing_username(self):
        data_nouname = json.dumps({"password": "foo",
                                   "email": "john@example.com"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data_nouname,
                                    content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual("username is required",
                         server_resp["message"])

    def test_register_missing_email(self):
        data_noemail = json.dumps({"password": "foo", "username": "johndoe"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data_noemail,
                                    content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual("email is required",
                         server_resp['message'])

    def test_register_missing_password(self):
        data_nopass = json.dumps({"email": "foo@example.com",
                                  "username": "johndoe"})
        url = "api/v1/auth/register"
        response = self.client.post(url, data=data_nopass,
                                    content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual("password is required",
                         server_resp["message"])


class BucketlistUserLoginTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        user = Users(username="johndoe", email="john@example.com",
                     password="foobar")
        db.session.add(user)
        db.session.commit()
        self.mime_type = "application/json"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_login_successful(self):
        details = json.dumps({"username": "johndoe", "password": "foobar"})
        url = "api/v1/auth/login"
        response = self.client.post(url, data=details, content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(server_resp["token"]) > 20)

    def test_user_login_wrong_details(self):
        details = json.dumps({"username": "john", "password": "foobar"})
        url = "api/v1/auth/login"
        response = self.client.post(url, data=details, content_type=self.mime_type)
        server_resp = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual("wrong username password combination",
                         server_resp["message"])

    def test_user_login_missing_details(self):
        no_uname = json.dumps({"password": "foobar"})
        url = "api/v1/auth/login"
        response_nn = self.client.post(url, data=no_uname,
                                       content_type=self.mime_type)
        server_respnn = json.loads(response_nn.data)
        self.assertEqual(response_nn.status_code, 403)
        self.assertEqual("username required",
                         server_respnn["message"])

        no_pass = json.dumps({"username": "foo"})
        response_np = self.client.post(url, data=no_pass,
                                       content_type=self.mime_type)
        server_respnp = json.loads(response_np.data)
        self.assertEqual(response_np.status_code, 403)
        self.assertEqual("password required",
                         server_respnp["message"])
