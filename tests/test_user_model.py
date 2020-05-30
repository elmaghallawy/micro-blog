import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    """class for User model Tests"""

    def setUp(self):
        self.user = User(password='cat')

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
