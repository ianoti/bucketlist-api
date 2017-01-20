import unittest
from flask import current_app
from app import create_app, db
from app.models import Users


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_in_testing_mode(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_password_setter(self):
        u = Users(password='cat')
        self.assertTrue(u.pass_hash is not None)

    def test_no_password_getter(self):
        u = Users(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = Users(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = Users(password='cat')
        u2 = Users(password='cat')
        self.assertTrue(u.pass_hash != u2.pass_hash)
