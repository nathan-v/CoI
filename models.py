from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from typing import TYPE_CHECKING, Optional
import hashlib
import markdown

# Initialize Flask-SQLAlchemy (this will be initialized in app.py)
db = SQLAlchemy()

# Association table for User-Group relationships
user_group_association = db.Table(
    "user_group_association",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
)

# Association table for Group-Group relationships (hierarchical groups)
group_group_association = db.Table(
    "group_group_association",
    db.Column(
        "parent_group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True
    ),
    db.Column(
        "child_group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True
    ),
)

# Association table for Incident-User access permissions (for sensitive incidents)
incident_user_access = db.Table(
    "incident_user_access",
    db.Column(
        "incident_id", db.Integer, db.ForeignKey("incident.id"), primary_key=True
    ),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)

# Association table for Incident-Group access permissions (for sensitive incidents)
incident_group_access = db.Table(
    "incident_group_access",
    db.Column(
        "incident_id", db.Integer, db.ForeignKey("incident.id"), primary_key=True
    ),
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
)


# User model with enhanced authentication support
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(
        db.String(255), nullable=True
    )  # Nullable for external auth
    auth_provider = db.Column(
        db.String(50), nullable=True
    )  # 'local', 'google', 'github', etc.
    auth_provider_id = db.Column(
        db.String(255), nullable=True
    )  # External provider user ID
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    groups = db.relationship("Group", secondary=user_group_association, backref="users")

    def set_password(self, password: str) -> None:
        """Set password hash for local authentication"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password for local authentication"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_external_authenticated(self) -> bool:
        """Check if user is authenticated via external provider"""
        return self.auth_provider is not None and self.auth_provider != "local"

    @staticmethod
    def get_or_create_external_user(
        auth_provider: str,
        auth_provider_id: str,
        username: str,
        email: Optional[str] = None,
    ) -> "User":
        """Get or create a user from external authentication provider"""
        # Try to find existing user by external auth provider and ID
        user = User.query.filter_by(
            auth_provider=auth_provider, auth_provider_id=auth_provider_id
        ).first()
        if user:
            return user

        # If not found, create new user with external authentication
        user = User(
            username=username,
            email=email,
            auth_provider=auth_provider,
            auth_provider_id=auth_provider_id,
            password_hash=None,  # No local password for external auth
        )
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# Group model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Owner relationship
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", foreign_keys=[owner_id])

    # Self-referential relationship for group hierarchies
    parent_groups = db.relationship(
        "Group",
        secondary=group_group_association,
        primaryjoin=id == group_group_association.c.child_group_id,
        secondaryjoin=id == group_group_association.c.parent_group_id,
        backref="child_groups",
    )

    def __repr__(self) -> str:
        return f"<Group {self.name}>"


# Incident model
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    why1 = db.Column(db.Text, nullable=True)
    why2 = db.Column(db.Text, nullable=True)
    why3 = db.Column(db.Text, nullable=True)
    why4 = db.Column(db.Text, nullable=True)
    why5 = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="open", nullable=False)
    security_level = db.Column(db.String(20), default="private", nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User", foreign_keys=[creator_id])

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User", foreign_keys=[owner_id])

    assigned_group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=True)
    assigned_group = db.relationship("Group")

    # Access permissions for sensitive incidents
    allowed_users = db.relationship(
        "User", secondary=incident_user_access, backref="accessible_incidents"
    )
    allowed_groups = db.relationship(
        "Group", secondary=incident_group_access, backref="accessible_incidents"
    )

    def __repr__(self) -> str:
        return f"<Incident {self.title}>"

    @property
    def summary_html(self) -> str:
        """Convert markdown summary to HTML for display"""
        if not self.summary:
            return ""
        return markdown.markdown(self.summary, extensions=["fenced_code", "tables"])


# Action Item model
class ActionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    tracking_link = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default="open", nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"), nullable=False)
    incident = db.relationship("Incident", backref="action_items")

    assigned_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_user = db.relationship("User", foreign_keys=[assigned_user_id])

    @property
    def summary_html(self) -> str:
        """Convert markdown summary to HTML for display"""
        if not self.summary:
            return ""
        return markdown.markdown(self.summary, extensions=["fenced_code", "tables"])
