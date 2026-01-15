import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app, db, load_user
from models import User
from flask import Flask
from werkzeug.security import generate_password_hash


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test app with testing configuration
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SECRET_KEY"] = "test-secret-key"

        # Create test client
        self.client = self.app.test_client()

        # Create app context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create database tables
        db.create_all()

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model_creation(self):
        """Test that User model can be created properly."""
        # Test creating a user with local authentication
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("password123"),
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertIsNotNone(user.password_hash)
        self.assertIsNone(user.auth_provider)
        self.assertIsNone(user.auth_provider_id)

    def test_user_external_auth_creation(self):
        """Test that User model can be created with external authentication."""
        # Test creating a user with external authentication
        user = User(
            username="externaluser",
            email="external@example.com",
            auth_provider="google",
            auth_provider_id="123456789",
            password_hash=None,
        )

        self.assertEqual(user.username, "externaluser")
        self.assertEqual(user.auth_provider, "google")
        self.assertEqual(user.auth_provider_id, "123456789")
        self.assertIsNone(user.password_hash)

    def test_user_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = User(username="testuser")
        password = "password123"
        user.set_password(password)

        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_external_authentication_check(self):
        """Test that external authentication check works correctly."""
        # Local user
        local_user = User(
            username="localuser", password_hash=generate_password_hash("password123")
        )

        # External user
        external_user = User(
            username="externaluser",
            auth_provider="google",
            auth_provider_id="123456789",
        )

        self.assertFalse(local_user.is_external_authenticated())
        self.assertTrue(external_user.is_external_authenticated())

    def test_user_get_or_create_external_user(self):
        """Test the get_or_create_external_user utility method."""
        # Test creating a new external user
        user = User.get_or_create_external_user(
            auth_provider="github",
            auth_provider_id="github123",
            username="githubuser",
            email="github@example.com",
        )

        self.assertEqual(user.username, "githubuser")
        self.assertEqual(user.auth_provider, "github")
        self.assertEqual(user.auth_provider_id, "github123")
        self.assertEqual(user.email, "github@example.com")

        # Test retrieving the same user (should return existing)
        existing_user = User.get_or_create_external_user(
            auth_provider="github",
            auth_provider_id="github123",
            username="githubuser",
            email="github@example.com",
        )

        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.username, existing_user.username)

    def test_user_loader(self):
        """Test that user loader works correctly."""
        user = User(
            username="loaderuser", password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        loaded_user = load_user(str(user.id))
        self.assertEqual(loaded_user.id, user.id)
        self.assertEqual(loaded_user.username, user.username)

    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config["TESTING"])

    def test_okta_login_route_exists(self):
        """Test that Okta login route exists."""
        response = self.client.get("/login/oauth2/okta")
        # This should return a 200 status code (or redirect)
        self.assertIn(response.status_code, [200, 302])

    def test_cognito_login_route_exists(self):
        """Test that Cognito login route exists."""
        response = self.client.get("/login/oauth2/cognito")
        # This should return a 200 status code (or redirect)
        self.assertIn(response.status_code, [200, 302])

    def test_user_external_auth_methods(self):
        """Test that external authentication methods work."""
        with self.app.app_context():
            # Test creating external user
            user = User.get_or_create_external_user(
                auth_provider="google",
                auth_provider_id="test_google_id",
                username="testuser",
                email="test@example.com",
            )

            self.assertEqual(user.auth_provider, "google")
            self.assertEqual(user.auth_provider_id, "test_google_id")
            self.assertEqual(user.username, "testuser")
            self.assertEqual(user.email, "test@example.com")

            # Test retrieving existing user
            existing_user = User.get_or_create_external_user(
                auth_provider="google",
                auth_provider_id="test_google_id",
                username="testuser",
                email="test@example.com",
            )

            self.assertEqual(user.id, existing_user.id)

    def test_simple_auth_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = User(username="testuser")
        password = "password123"
        user.set_password(password)

        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_simple_auth_external_authentication_check(self):
        """Test that external authentication check works correctly."""
        # Local user
        local_user = User(username="localuser", password_hash="hashed_password")

        # External user
        external_user = User(
            username="externaluser", auth_provider="google", auth_provider_id="12345"
        )

        self.assertFalse(local_user.is_external_authenticated())
        self.assertTrue(external_user.is_external_authenticated())

    def test_oauth2_login_routes(self):
        """Test OAuth2 login routes."""
        response = self.client.get("/login/oauth2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/login/oauth2/google")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/login/oauth2/github")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/login/oauth2/okta")
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/login/oauth2/cognito")
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()
