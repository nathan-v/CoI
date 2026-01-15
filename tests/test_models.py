import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app, db
from models import User, Group, Incident, ActionItem
from werkzeug.security import generate_password_hash


class TestModels(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for model tests."""
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

    def test_group_model_creation(self):
        """Test that Group model can be created properly."""
        group = Group(name="Test Group", description="Test Description")

        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.description, "Test Description")

    def test_incident_model_creation(self):
        """Test that Incident model can be created properly."""
        # Create a test user
        user = User(
            username="testuser", password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        incident = Incident(
            title="Test Incident", summary="Test Summary", creator_id=user.id
        )

        self.assertEqual(incident.title, "Test Incident")
        self.assertEqual(incident.summary, "Test Summary")
        self.assertEqual(incident.creator_id, user.id)

    def test_action_item_model_creation(self):
        """Test that ActionItem model can be created properly."""
        # Create test user and incident
        user = User(
            username="testuser", password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        incident = Incident(
            title="Test Incident", summary="Test Summary", creator_id=user.id
        )
        db.session.add(incident)
        db.session.commit()

        action_item = ActionItem(
            title="Test Action Item",
            summary="Test Summary",
            incident_id=incident.id,
            assigned_user_id=user.id,
        )

        self.assertEqual(action_item.title, "Test Action Item")
        self.assertEqual(action_item.summary, "Test Summary")
        self.assertEqual(action_item.incident_id, incident.id)
        self.assertEqual(action_item.assigned_user_id, user.id)


if __name__ == "__main__":
    unittest.main()
