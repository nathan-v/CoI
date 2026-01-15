import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app, db
from models import User, Incident, ActionItem
from werkzeug.security import generate_password_hash


class TestIncidents(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for incidents tests."""
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

    def test_incident_creation(self):
        """Test incident creation functionality."""
        # Create a test user
        user = User(
            username="testuser", password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        # Create incident
        incident = Incident(
            title="Test Incident", summary="Test Summary", creator_id=user.id
        )
        db.session.add(incident)
        db.session.commit()

        # Verify incident was created
        retrieved_incident = Incident.query.get(incident.id)
        self.assertEqual(retrieved_incident.title, "Test Incident")
        self.assertEqual(retrieved_incident.summary, "Test Summary")
        self.assertEqual(retrieved_incident.creator_id, user.id)

    def test_incident_with_action_items(self):
        """Test incidents with associated action items."""
        # Create test user
        user = User(
            username="testuser", password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        # Create incident
        incident = Incident(
            title="Test Incident", summary="Test Summary", creator_id=user.id
        )
        db.session.add(incident)
        db.session.commit()

        # Create action item
        action_item = ActionItem(
            title="Test Action Item",
            summary="Test Summary",
            incident_id=incident.id,
            assigned_user_id=user.id,
        )
        db.session.add(action_item)
        db.session.commit()

        # Verify relationship
        retrieved_incident = Incident.query.get(incident.id)
        self.assertEqual(len(retrieved_incident.action_items), 1)
        self.assertEqual(retrieved_incident.action_items[0].title, "Test Action Item")


if __name__ == "__main__":
    unittest.main()
