from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from models import User, Group, Incident, ActionItem, db
from typing import List
from decorators import admin_required, login_required
from logging_config import get_logger

# Admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

logger = get_logger(None)


@admin_bp.route("/")
@admin_required
def admin_panel():
    """Admin dashboard"""
    # Get counts for dashboard
    user_count = User.query.count()
    admin_count = User.query.filter_by(is_admin=True).count()
    group_count = Group.query.count()
    incident_count = Incident.query.count()
    action_item_count = ActionItem.query.count()

    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        admin_count=admin_count,
        group_count=group_count,
        incident_count=incident_count,
        action_item_count=action_item_count,
    )


@admin_bp.route("/users")
@admin_required
def admin_users():
    """Manage users"""
    users: List[User] = User.query.all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def admin_user_create():
    """Create a new user"""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form.get("email")
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        is_admin = request.form.get("is_admin") == "on"
        group_ids = request.form.getlist("group_ids")

        # Validate form data
        if not username:
            flash("Username is required.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        if not email:
            flash("Email is required.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        if not password or not confirm_password:
            flash("All password fields are required.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered.")
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

        # Create new user
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        user.auth_provider = "local"

        # Assign user to groups if specified
        if group_ids:
            groups = Group.query.filter(Group.id.in_(group_ids)).all()
            user.groups.extend(groups)

        try:
            db.session.add(user)
            db.session.commit()
            flash("User created successfully!", "success")
            return redirect(url_for("admin.admin_users"))
        except Exception as e:
            db.session.rollback()
            logger.debug(e)
            flash(
                "An error occurred while creating the user. Please try again.", "error"
            )
            return render_template(
                "admin/user_form.html",
                is_edit=False,
                user={"username": username, "email": email},
                groups=Group.query.all(),
            )

    return render_template(
        "admin/user_form.html", is_edit=False, groups=Group.query.all()
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def admin_user_edit(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        username = request.form["username"]
        email = request.form.get("email")
        is_admin = request.form.get("is_admin") == "on"
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        group_ids = request.form.getlist("group_ids")

        # Validate form data
        if not username:
            flash("Username is required.")
            return render_template(
                "admin/user_form.html",
                is_edit=True,
                user=user,
                groups=Group.query.all(),
            )

        # Check if username already exists (excluding current user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash("Username already exists.")
            return render_template(
                "admin/user_form.html",
                is_edit=True,
                user=user,
                groups=Group.query.all(),
            )

        # Check if email already exists (if provided, excluding current user)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != user_id:
                flash("Email already registered.")
                return render_template(
                    "admin/user_form.html",
                    is_edit=True,
                    user=user,
                    groups=Group.query.all(),
                )

        # Update user data
        user.username = username
        user.email = email
        user.is_admin = is_admin
        if password and password == confirm_password and len(password) >= 6:
            user.set_password(password)
        elif password and (password != confirm_password or len(password) < 6):
            flash(
                "Password must be at least 6 characters long and match the confirmation.",
                "error",
            )
            return render_template(
                "admin/user_form.html",
                is_edit=True,
                user=user,
                groups=Group.query.all(),
            )

        # Update group associations
        # Clear existing group associations
        user.groups.clear()
        # Add new group associations if specified
        if group_ids:
            groups = Group.query.filter(Group.id.in_(group_ids)).all()
            user.groups.extend(groups)

        try:
            db.session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("admin.admin_users"))
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while updating the user. Please try again.", "error"
            )
            return render_template(
                "admin/user_form.html",
                is_edit=True,
                user=user,
                groups=Group.query.all(),
            )

    return render_template(
        "admin/user_form.html", is_edit=True, user=user, groups=Group.query.all()
    )


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def admin_user_delete(user_id):
    """Delete a user (only admins can delete)"""
    # Only admins can delete users
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash("You cannot delete yourself.", "error")
        return redirect(url_for("admin.admin_users"))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the user. Please try again.", "error")

    return redirect(url_for("admin.admin_users"))


@admin_bp.route("/groups")
@admin_required
def admin_groups():
    """Manage groups"""
    groups: List[Group] = Group.query.all()
    return render_template("admin/groups.html", groups=groups)


@admin_bp.route("/groups/create", methods=["GET", "POST"])
@login_required
def admin_group_create():
    """Create a new group"""
    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description")
        owner_id = request.form.get("owner_id")
        parent_group_id = request.form.get("parent_group_id")
        if owner_id:
            owner_id = int(owner_id)
        else:
            owner_id = None
        if parent_group_id:
            parent_group_id = int(parent_group_id)
        else:
            parent_group_id = None

        # Validate form data
        if not name:
            flash("Name is required.")
            return render_template("admin/group_form.html", is_edit=False)

        # Check if group name already exists
        existing_group = Group.query.filter_by(name=name).first()
        if existing_group:
            flash("Group name already exists.")
            return render_template("admin/group_form.html", is_edit=False)

        # Create new group
        group = Group(name=name, description=description)
        if owner_id:
            group.owner_id = owner_id
        else:
            group.owner_id = None
        if parent_group_id:
            # Add parent group relationship
            parent_group = Group.query.get(parent_group_id)
            if parent_group:
                group.parent_groups.append(parent_group)

        try:
            db.session.add(group)
            db.session.commit()
            flash("Group created successfully!", "success")
            return redirect(url_for("admin.admin_groups"))
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while creating the group. Please try again.", "error"
            )
            return render_template("admin/group_form.html", is_edit=False)

    # Get all users for owner selection and all groups for parent selection
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        "admin/group_form.html", is_edit=False, users=users, groups=groups
    )


@admin_bp.route("/groups/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def admin_group_edit(group_id):
    """Edit an existing group"""
    group = Group.query.get_or_404(group_id)
    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description")
        owner_id = request.form.get("owner_id")
        parent_group_id = request.form.get("parent_group_id")
        if owner_id:
            owner_id = int(owner_id)
        else:
            owner_id = None
        if parent_group_id:
            parent_group_id = int(parent_group_id)
        else:
            parent_group_id = None

        # Validate form data
        if not name:
            flash("Name is required.")
            return render_template(
                "admin/group_form.html",
                is_edit=True,
                group=group,
                users=User.query.all(),
                groups=Group.query.all(),
            )

        # Check if group name already exists (excluding current group)
        existing_group = Group.query.filter_by(name=name).first()
        if existing_group and existing_group.id != group_id:
            flash("Group name already exists.")
            return render_template(
                "admin/group_form.html",
                is_edit=True,
                group=group,
                users=User.query.all(),
                groups=Group.query.all(),
            )

        # Update group data
        group.name = name
        group.description = description
        group.owner_id = owner_id if owner_id else None
        # Handle parent group relationship
        if parent_group_id:
            # Clear existing parent groups and add the new one
            group.parent_groups.clear()
            parent_group = Group.query.get(parent_group_id)
            if parent_group:
                group.parent_groups.append(parent_group)
        else:
            # Clear parent groups if none selected
            group.parent_groups.clear()

        try:
            db.session.commit()
            flash("Group updated successfully!", "success")
            return redirect(url_for("admin.admin_groups"))
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while updating the group. Please try again.", "error"
            )
            return render_template(
                "admin/group_form.html",
                is_edit=True,
                group=group,
                users=User.query.all(),
                groups=Group.query.all(),
            )

    # Get all users for owner selection and all groups for parent selection
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        "admin/group_form.html", is_edit=True, group=group, users=users, groups=groups
    )


@admin_bp.route("/groups/<int:group_id>/delete", methods=["POST"])
@login_required
def admin_group_delete(group_id):
    """Delete a group (only admins can delete)"""
    # Only admins can delete groups
    if not current_user.is_admin:
        abort(403)

    group = Group.query.get_or_404(group_id)
    try:
        db.session.delete(group)
        db.session.commit()
        flash("Group deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the group. Please try again.", "error")

    return redirect(url_for("admin.admin_groups"))


@admin_bp.route("/incidents")
@admin_required
def admin_incidents():
    """Manage incidents"""
    incidents: List[Incident] = Incident.query.all()
    return render_template("admin/incidents.html", incidents=incidents)


@admin_bp.route("/incidents/<int:incident_id>/delete", methods=["POST"])
@login_required
def admin_incident_delete(incident_id):
    """Delete an incident (only admins can delete)"""
    # Only admins can delete incidents
    if not current_user.is_admin:
        abort(403)

    incident = Incident.query.get_or_404(incident_id)
    try:
        db.session.delete(incident)
        db.session.commit()
        flash("Incident deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(
            "An error occurred while deleting the incident. Please try again.", "error"
        )

    return redirect(url_for("admin.admin_incidents"))


@admin_bp.route("/action_items")
@admin_required
def admin_action_items():
    """Manage action items"""
    action_items: List[ActionItem] = ActionItem.query.all()
    return render_template("admin/action_items.html", action_items=action_items)


@admin_bp.route("/action_items/<int:action_item_id>/delete", methods=["POST"])
@login_required
def admin_action_item_delete(action_item_id):
    """Delete an action item (only admins can delete)"""
    # Only admins can delete action items
    if not current_user.is_admin:
        abort(403)

    action_item = ActionItem.query.get_or_404(action_item_id)
    try:
        db.session.delete(action_item)
        db.session.commit()
        flash("Action item deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(
            "An error occurred while deleting the action item. Please try again.",
            "error",
        )

    return redirect(url_for("admin.admin_action_items"))
