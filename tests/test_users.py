from setup_test import BaseTestClass
from app.models import User
import json


class UserRegisterTest(BaseTestClass):
    """ the tests for user registration """

    def test_user_registration(self):
        """ test that user can register with valid details"""
        old = User.query.count()
        data = json.dumps({"username": "johnman", "password": "johnman",
                           "email": "johnman@example.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        new = User.query.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(new-old, 1)
        self.assertEqual(resp_data["message"], ("user johnman has been "
                                                "successfully added"))

    def test_register_existing_username(self):
        """ test that all usernames are unique and all stored in lowercase """
        data = json.dumps({"username": "johndoe", "password": "johnman",
                           "email": "johndoe@example.com"})
        data_name = json.dumps({"username": "JohnDoe", "password": "johnman",
                                "email": "johndoe@example.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        response_cap = self.app.post("/api/v1/auth/register", data=data,
                                     content_type=self.mime_type)
        resp_data = json.loads(response.data)
        respcap_data = json.loads(response_cap.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_cap.status_code, 403)
        self.assertEqual(User.query.count(), 2)
        self.assertEqual(resp_data["message"], "username already taken")
        self.assertEqual(respcap_data["message"], "username already taken")

    def test_missing_details_for_register(self):
        """ test that post request validates the existence of username,
        password and email fields"""
        data_nouser = json.dumps({"password": "johnman",
                                  "email": "john@example.com"})
        data_nopass = json.dumps({"username": "johnman",
                                  "email": "john@example.com"})
        data_noemail = json.dumps({"username": "johnman",
                                   "password": "johnman"})
        response_nouser = self.app.post("/api/v1/auth/register",
                                        data=data_nouser,
                                        content_type=self.mime_type)
        response_nopass = self.app.post("/api/v1/auth/register",
                                        data=data_nopass,
                                        content_type=self.mime_type)
        response_noemail = self.app.post("/api/v1/auth/register",
                                         data=data_noemail,
                                         content_type=self.mime_type)
        resp_nouser = json.loads(response_nouser.data)
        resp_nopass = json.loads(response_nopass.data)
        resp_noemail = json.loads(response_noemail.data)
        self.assertListEqual([400, 400, 400], [response_nouser.status_code,
                                               response_nopass.status_code,
                                               response_noemail.status_code])
        self.assertEqual(resp_nouser["message"]["username"],
                         "username required")
        self.assertEqual(resp_nopass["message"]["password"],
                         "password required")
        self.assertEqual(resp_noemail["message"]["email"],
                         "email required")

    def test_bad_details_for_registration(self):
        """test that username can't contain special characters"""
        data = json.dumps({"username": "#@!^", "password": "foobar",
                           "email": "foobar"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(400, response.status_code)
        self.assertIn("allowed in username", resp_data["message"])
        self.assertEqual(User.query.count(), 2)

    def test_blank_arguments_not_allowed(self):
        """test that registration doesn't accept blank arguments """
        blnk_nme = json.dumps({"username": "", "password": "foobar",
                               "email": "foobar"})
        blnk_pass = json.dumps({"username": "", "password": "",
                                "email": "foobar"})
        blnk_mail = json.dumps({"username": "", "password": "",
                                "email": "foobar"})
        resp_nme = self.app.post("/api/v1/auth/register", data=blnk_nme,
                                 content_type=self.mime_type)
        resp_pass = self.app.post("/api/v1/auth/register", data=blnk_pass,
                                  content_type=self.mime_type)
        resp_mail = self.app.post("/api/v1/auth/register", data=blnk_mail,
                                  content_type=self.mime_type)
        data_nme = json.loads(resp_nme.data)
        data_pass = json.loads(resp_pass.data)
        data_mail = json.loads(resp_mail.data)
        self.assertListEqual([400, 400, 400], [resp_nme.status_code,
                                               resp_pass.status_code,
                                               resp_mail.status_code])
        self.assertListEqual(["no blank fields allowed",
                              "no blank fields allowed"],
                             [data_nme["message"], data_pass["message"]])
        self.assertEqual(User.query.count(), 2)

    def test_email_field_basic_validation(self):
        """test that the @ symbol must be present as a test of the email
        validation"""
        data = json.dumps({"username": "johnman", "password": "johnman",
                           "email": "johnmanexample.com"})
        response = self.app.post("/api/v1/auth/register", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(400, response.status_code)
        self.assertEqual("email is invalid", resp_data["message"])

    def test_password_salts_are_random(self):
        """ test that hashing algorithm doesn't store equal passwords with an
        equal hash """
        user_one = User.query.filter_by(id=1).first()
        user_two = User.query.filter_by(id=2).first()
        self.assertTrue(user_one.pass_hash != user_two.pass_hash)

    def test_user_password_cant_be_read(self):
        """test that password attribute can't be directly accessed, is read
        only"""
        user_one = User.query.filter_by(id=1).first()
        with self.assertRaises(AttributeError):
            user_one.password


class UserLoginTest(BaseTestClass):
    """the tests for user login"""
    def test_successful_login(self):
        """test that user can login with valid details and gets token"""
        data = json.dumps({"username": "johndoe", "password": "foobar"})
        response = self.app.post("api/v1/auth/login", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(resp_data["token"]) > 20)

    def test_unregistered_user_cant_get_token(self):
        """ test that unregistered users can't obtain a token"""
        data = json.dumps({"username": "foobar", "password": "foobar"})
        response = self.app.post("api/v1/auth/login", data=data,
                                 content_type=self.mime_type)
        resp_data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp_data["message"], "wrong login details")

    def test_missing_details_login(self):
        """ test that API catches missing keys errors """
        data_noname = json.dumps({"password": "foobar"})
        data_nopass = json.dumps({"username": "johndoe"})
        resp_noname = self.app.post("api/v1/auth/login", data=data_noname,
                                    content_type=self.mime_type)
        resp_nopass = self.app.post("api/v1/auth/login", data=data_nopass,
                                    content_type=self.mime_type)
        resp_nonamedata = json.loads(resp_noname.data)
        resp_nopassdata = json.loads(resp_nopass.data)
        self.assertListEqual([400, 400], [resp_noname.status_code,
                                          resp_nopass.status_code])
        self.assertEqual(resp_nonamedata["message"]["username"], ("username"
                                                                  " required"))
        self.assertEqual(resp_nopassdata["message"]["password"], ("password"
                                                                  " required"))
