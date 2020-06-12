import unittest
import time
from app.models import User
from app import create_app, db


class UserModelTestCase(unittest.TestCase):
    """class for User model Tests"""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(password='cat')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """test setting the password and generating
        hash for it"""

        self.assertTrue(self.user.password_hash is not None)

    def test_no_password_getter(self):
        """test that password cannot be read"""
        with self.assertRaises(AttributeError):
            self.user.password

    def test_password_verification(self):
        """test password verification works"""
        self.assertTrue(self.user.verify_password('cat'))
        self.assertFalse(self.user.verify_password('dog'))

    def test_password_salts_are_random(self):
        u2 = User(password='cat')
        self.assertTrue(self.user.password_hash != u2.password_hash)

    def test_confirmation_valid_token(self):
        """test valid confirmation token"""
        token = self.user.generate_confirmation_token()
        self.assertTrue(self.user.confirm(token))

    def test_confirmation_invalid_token(self):
        """test invalid confirmation token"""
        u2 = User(password='dog')
        db.session.add(self.user)
        db.session.add(u2)
        db.session.commit()
        token = self.user.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        """test expired confirmation token"""
        token = self.user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(self.user.confirm(token))
