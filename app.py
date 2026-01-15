import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
from config import config
from models import db, User
from typing import Optional
import markdown

from admin_panel import admin_bp
from incidents import incidents_bp
from action_items import action_items_bp
from auth import auth_bp
from logging_config import setup_logging

# Import Flask-Dance for OAuth2
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github

# Initialize OAuth2 blueprints
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="google_login",
)
github_bp = make_github_blueprint(
    client_id=os.environ.get("GITHUB_CLIENT_ID"),
    client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
    scope=["user:email"],
    redirect_to="github_login",
)

# Create the Flask app
app = Flask(__name__)
app.config.from_object(config["default"])
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-for-testing")
setup_logging(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

# Initialize Flask-SQLAlchemy
db.init_app(app)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.query.get(int(user_id))


# Define the home route
@app.route("/")
def home() -> str:
    return render_template("home.html")


# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(incidents_bp)
app.register_blueprint(action_items_bp)
app.register_blueprint(auth_bp)

# Register OAuth2 blueprints
app.register_blueprint(google_bp, url_prefix="/login/google")
app.register_blueprint(github_bp, url_prefix="/login/github")

# Create database tables
with app.app_context():
    # Check if tables exist before creating
    try:
        # Check if tables already exist to prevent overwriting
        if len(db.metadata.tables) == 0:
            # Create tables only if none exist
            # This prevents data loss on each application restart
            db.create_all()
            print("Database initialized")
        else:
            print("Database tables already exist, skipping initialization")
    except Exception as e:
        print(f"Database creation error: {e}")
        # Continue with app initialization


# Add CLI command for creating admin user
@app.cli.command()
def create_admin():
    """Create a new admin user"""
    from getpass import getpass

    print("Creating new admin user...")

    # Get user input
    username = input("Username: ")
    email = input("Email (optional): ") or None
    password = getpass("Password: ")
    confirm_password = getpass("Confirm password: ")

    # Validate password
    if password != confirm_password:
        print("Error: Passwords do not match")
        return

    if len(password) < 6:
        print("Error: Password must be at least 6 characters long")
        return

    # Create user in database
    with app.app_context():
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("Error: Username already exists")
            return

        # Check if email already exists (if provided)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print("Error: Email already registered")
                return

        # Create new admin user
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        user.auth_provider = "local"

        try:
            db.session.add(user)
            db.session.commit()
            print(f"Success: Admin user '{username}' created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error: An error occurred while creating the user: {e}")


# Run the app if this file is executed directly
if __name__ == "__main__":
    # Add markdown filter for templates
    app.jinja_env.filters["markdown"] = lambda text: markdown.markdown(
        text, extensions=["fenced_code", "tables"]
    )
    app.run(debug=True)
