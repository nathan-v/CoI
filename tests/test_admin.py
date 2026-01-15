import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app, db
from models import User
from werkzeug.security import generate_password_hash


class TestAdminPages(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for admin pages tests."""
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test-secret-key"

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        """Tear down test fixtures."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_admin_user_creation(self):
        """Test that admin user can be created."""
        admin_user = User(
            username="adminuser",
            password_hash=generate_password_hash("password123"),
            is_admin=True,
        )
        db.session.add(admin_user)
        db.session.commit()

        retrieved_user = User.query.get(admin_user.id)
        self.assertTrue(retrieved_user.is_admin)
        self.assertEqual(retrieved_user.username, "adminuser")

    def test_regular_user_creation(self):
        """Test that regular user can be created."""
        regular_user = User(
            username="regularuser",
            password_hash=generate_password_hash("password123"),
            is_admin=False,
        )
        db.session.add(regular_user)
        db.session.commit()

        retrieved_user = User.query.get(regular_user.id)
        self.assertFalse(retrieved_user.is_admin)
        self.assertEqual(retrieved_user.username, "regularuser")


if __name__ == "__main__":
    unittest.main()
