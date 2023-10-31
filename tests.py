from datetime import datetime, timedelta
import unittest
from flask import Flask
from app import db, mail
from app.models import User


def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config['TESTING'] = True
    return app


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_password_hashing(self):
        with self.app.app_context():
            u = User(username='bvpn')
            u.set_password('123123')
            self.assertFalse(u.check_password('123'))
            self.assertTrue(u.check_password('123123'))


if __name__ == '__main__':
    unittest.main(verbosity=2)

