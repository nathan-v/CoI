from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
)
from decorators import login_required, admin_required
from models import db, User

# Create the authentication blueprint
auth_bp = Blueprint("auth", __name__)


# User loader for Flask-Login
@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Find user by username
        user = User.query.filter_by(username=username).first()

        # Check local authentication first
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Invalid username or password")

    return render_template(
        "login.html",
        local_registration_enabled=current_app.config.get(
            "LOCAL_REGISTRATION_ENABLED", True
        ),
    )


# Registration route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Check if local registration is enabled
    if not current_app.config.get("LOCAL_REGISTRATION_ENABLED", True):
        flash("Local registration is not enabled.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form.get("email")
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Validate form data
        if not username or not password or not confirm_password:
            flash("All fields are required.")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return render_template("register.html")

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return render_template("register.html")

        # Check if email already exists (if provided)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash("Email already registered.")
                return render_template("register.html")

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        user.auth_provider = "local"

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while creating your account. Please try again.",
                "error",
            )
            return render_template("register.html")

    return render_template("register.html")


# OAuth2 login route (placeholder for external auth)
@auth_bp.route("/login/oauth2")
def oauth2_login():
    # This would be implemented with a library like Flask-Dance
    # For now, we'll redirect to a placeholder page
    return render_template("oauth2_login.html")


# Google OAuth2 login route
@auth_bp.route("/login/oauth2/google")
def login_oauth2_google():
    # This would be implemented with Flask-Dance
    # For now, we'll redirect to a placeholder page
    return "Google OAuth2 login would be implemented here"


# GitHub OAuth2 login route
@auth_bp.route("/login/oauth2/github")
def login_oauth2_github():
    # This would be implemented with Flask-Dance
    # For now, we'll redirect to a placeholder page
    return "GitHub OAuth2 login would be implemented here", 200


# Okta OAuth2 login route
@auth_bp.route("/login/oauth2/okta")
def login_oauth2_okta():
    # Custom Okta implementation without Flask-Dance
    # This would redirect to Okta authorization endpoint
    okta_org = current_app.config.get("OKTA_ORG")
    client_id = current_app.config.get("OKTA_CLIENT_ID")
    if not okta_org or not client_id:
        flash("Okta authentication not configured properly")
        return redirect(url_for("auth.login"))

    # Build Okta authorization URL
    # This is a simplified example - in production, you'd want to use proper OAuth2 flow
    auth_url = f"{okta_org}/oauth2/v1/authorize"
    redirect_uri = url_for("okta_login", _external=True)
    scope = "openid profile email"

    # For demonstration purposes, we'll redirect to a placeholder page
    # In a real implementation, this would redirect to Okta's authorization endpoint
    return render_template(
        "oauth2_login.html",
        provider="Okta",
        auth_url=auth_url,
        redirect_uri=redirect_uri,
        client_id=client_id,
        scope=scope,
    )


# AWS Cognito OAuth2 login route
@auth_bp.route("/login/oauth2/cognito")
def login_oauth2_cognito():
    # Custom Cognito implementation without Flask-Dance
    # This would redirect to Cognito authorization endpoint
    cognito_region = current_app.config.get("COGNITO_REGION")
    client_id = current_app.config.get("COGNITO_CLIENT_ID")
    user_pool = current_app.config.get("COGNITO_USER_POOL")
    if not cognito_region or not client_id or not user_pool:
        flash("Cognito authentication not configured properly")
        return redirect(url_for("auth.login"))

    # Build Cognito authorization URL
    # This is a simplified example - in production, you'd want to use proper OAuth2 flow
    auth_url = (
        f"https://{user_pool}.auth.{cognito_region}.amazoncognito.com/oauth2/authorize"
    )
    redirect_uri = url_for("cognito_login", _external=True)
    scope = "openid profile email"

    # For demonstration purposes, we'll redirect to a placeholder page
    # In a real implementation, this would redirect to Cognito's authorization endpoint
    return render_template(
        "oauth2_login.html",
        provider="Cognito",
        auth_url=auth_url,
        redirect_uri=redirect_uri,
        client_id=client_id,
        scope=scope,
    )


# OAuth2 callback routes
@auth_bp.route("/google/login")
def google_login():
    # Import here to avoid circular imports
    from flask_dance.contrib.google import google

    if not google.authorized:
        return redirect(url_for("google.login"))
    # Get user info from Google
    resp = google.get("/oauth2/v2/userinfo")
    if resp.status_code != 200:
        flash("Failed to fetch user info from Google")
        return redirect(url_for("auth.login"))
    user_info = resp.json()
    # Create or get user with external authentication
    user = User.get_or_create_external_user(
        auth_provider="google",
        auth_provider_id=user_info["sub"],
        username=user_info.get("name", user_info["email"].split("@")[0]),
        email=user_info["email"],
    )
    login_user(user)
    next_page = request.args.get("next")
    return redirect(next_page) if next_page else redirect(url_for("home"))


@auth_bp.route("/github/login")
def github_login():
    # Import here to avoid circular imports
    from flask_dance.contrib.github import github

    if not github.authorized:
        return redirect(url_for("github.login"))
    # Get user info from GitHub
    resp = github.get("/user")
    if resp.status_code != 200:
        flash("Failed to fetch user info from GitHub")
        return redirect(url_for("auth.login"))
    user_info = resp.json()
    # Get email from GitHub (they may be private)
    email_resp = github.get("/user/emails")
    email = None
    if email_resp.status_code == 200:
        emails = email_resp.json()
        # Get primary email (or first one)
        for e in emails:
            if e.get("primary", False):
                email = e["email"]
                break
        if not email and emails:
            email = emails[0]["email"]
    # Create or get user with external authentication
    user = User.get_or_create_external_user(
        auth_provider="github",
        auth_provider_id=str(user_info["id"]),
        username=user_info.get("name", user_info["login"]),
        email=(
            email or user_info["email"]
            if "email" in user_info
            else "noemail@example.com"
        ),
    )
    login_user(user)
    next_page = request.args.get("next")
    return redirect(next_page) if next_page else redirect(url_for("home"))


# Logout route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# Okta OAuth2 callback route (placeholder)
@auth_bp.route("/okta/login")
def okta_login():
    # This would handle the Okta OAuth2 callback
    # In a real implementation, this would verify the authorization code
    # and complete the authentication flow
    flash("Okta authentication would be implemented here")
    return redirect(url_for("auth.login"))


# AWS Cognito OAuth2 callback route (placeholder)
@auth_bp.route("/cognito/login")
def cognito_login():
    # This would handle the Cognito OAuth2 callback
    # In a real implementation, this would verify the authorization code
    # and complete the authentication flow
    flash("Cognito authentication would be implemented here")
    return redirect(url_for("auth.login"))
