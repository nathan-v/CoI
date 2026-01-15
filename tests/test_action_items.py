import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app, db
from models import User, Incident, ActionItem
from werkzeug.security import generate_password_hash


class TestActionItems(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for action items tests."""
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

    def test_action_item_creation(self):
        """Test action item creation functionality."""
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

        # Verify action item was created
        retrieved_action_item = ActionItem.query.get(action_item.id)
        self.assertEqual(retrieved_action_item.title, "Test Action Item")
        self.assertEqual(retrieved_action_item.summary, "Test Summary")
        self.assertEqual(retrieved_action_item.incident_id, incident.id)
        self.assertEqual(retrieved_action_item.assigned_user_id, user.id)


if __name__ == "__main__":
    unittest.main()
