from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Incident, User, Group, ActionItem, db
from typing import List

# Incidents blueprint
incidents_bp = Blueprint("incidents", __name__, url_prefix="/incidents")


@incidents_bp.route("/")
def incidents_list():
    """List all incidents"""
    # For logged-in users, show all incidents they have access to
    # Public incidents are visible to everyone
    # Private incidents are visible to creator, owner, and admins
    # Sensitive incidents are visible to creator, admins, and explicitly granted users

    if current_user.is_authenticated:
        # Users can see public incidents and incidents they have access to
        incidents = Incident.query.order_by(Incident.created_at.desc()).all()
        # Filter incidents based on access rights
        accessible_incidents = []
        for incident in incidents:
            # Handle cases where security_level might not exist (backward compatibility)
            # For now, default to private access for backward compatibility
            security_level = getattr(incident, "security_level", "private")

            if security_level == "public":
                accessible_incidents.append(incident)
            elif security_level == "private":
                if (
                    current_user == incident.creator
                    or current_user == incident.owner
                    or current_user.is_admin
                ):
                    accessible_incidents.append(incident)
            elif security_level == "sensitive":
                # Check if user has explicit access to sensitive incident
                has_access = False
                if current_user == incident.creator or current_user.is_admin:
                    has_access = True
                else:
                    try:
                        # Use database query to check explicit access for sensitive incidents
                        from models import incident_user_access

                        access_query = db.session.query(incident_user_access).filter(
                            incident_user_access.c.incident_id == incident.id,
                            incident_user_access.c.user_id == current_user.id,
                        )
                        if access_query.first():
                            has_access = True
                    except Exception:
                        # If there's an error accessing the relationship, deny access
                        pass

                if has_access:
                    accessible_incidents.append(incident)
        incidents = accessible_incidents
    else:
        # Non-authenticated users only see public incidents
        incidents = (
            Incident.query.filter_by(security_level="public")
            .order_by(Incident.created_at.desc())
            .all()
        )

    # Get all users and groups for filter dropdowns
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        "incidents/list.html",
        incidents=incidents,
        filter_type="all_open",
        users=users,
        groups=groups,
    )


@incidents_bp.route("/user/<int:user_id>")
@login_required
def incidents_by_user(user_id: int):
    """List incidents created or owned by a specific user"""
    # Get all incidents created or owned by this user
    incidents = (
        Incident.query.filter(
            (Incident.creator_id == user_id) | (Incident.owner_id == user_id)
        )
        .order_by(Incident.created_at.desc())
        .all()
    )

    # Filter incidents based on access rights for logged-in users
    if current_user.is_authenticated:
        accessible_incidents = []
        for incident in incidents:
            # Handle cases where security_level might not exist (backward compatibility)
            security_level = getattr(incident, "security_level", "private")

            if security_level == "public":
                accessible_incidents.append(incident)
            elif security_level == "private":
                if (
                    current_user == incident.creator
                    or current_user == incident.owner
                    or current_user.is_admin
                ):
                    accessible_incidents.append(incident)
            elif security_level == "sensitive":
                # Check if user has explicit access to sensitive incident
                has_access = False
                if current_user == incident.creator or current_user.is_admin:
                    has_access = True
                else:
                    try:
                        # Use database query to check explicit access for sensitive incidents
                        from models import incident_user_access

                        access_query = db.session.query(incident_user_access).filter(
                            incident_user_access.c.incident_id == incident.id,
                            incident_user_access.c.user_id == current_user.id,
                        )
                        if access_query.first():
                            has_access = True
                    except Exception:
                        # If there's an error accessing the relationship, deny access
                        pass
                if has_access:
                    accessible_incidents.append(incident)
        incidents = accessible_incidents
    else:
        # Non-authenticated users only see public incidents
        incidents = [i for i in incidents if i.security_level == "public"]

    # Get all users and groups for filter dropdowns
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        "incidents/list.html",
        incidents=incidents,
        filter_type="user",
        user_id=user_id,
        users=users,
        groups=groups,
    )


@incidents_bp.route("/group/<int:group_id>")
@login_required
def incidents_by_group(group_id: int):
    """List incidents assigned to a specific group (including nested groups)"""

    # Get all groups in the hierarchy (including nested groups)
    def get_all_child_groups(group_id: int) -> List[int]:
        """Recursively get all child groups"""
        child_groups = Group.query.filter(Group.parent_groups.any(id=group_id)).all()
        all_groups = [group_id]
        for child_group in child_groups:
            all_groups.extend(get_all_child_groups(child_group.id))
        return all_groups

    # Get all groups in the hierarchy
    all_group_ids = get_all_child_groups(group_id)

    # Get all incidents assigned to these groups - using proper SQLAlchemy syntax
    incidents = (
        Incident.query.filter(Incident.assigned_group_id.in_(all_group_ids))
        .order_by(Incident.created_at.desc())
        .all()
    )

    # Filter incidents based on access rights for logged-in users
    if current_user.is_authenticated:
        accessible_incidents = []
        for incident in incidents:
            # Handle cases where security_level might not exist (backward compatibility)
            security_level = getattr(incident, "security_level", "private")

            if security_level == "public":
                accessible_incidents.append(incident)
            elif security_level == "private":
                if (
                    current_user == incident.creator
                    or current_user == incident.owner
                    or current_user.is_admin
                ):
                    accessible_incidents.append(incident)
            elif security_level == "sensitive":
                # Check if user has explicit access to sensitive incident
                has_access = False
                if current_user == incident.creator or current_user.is_admin:
                    has_access = True
                else:
                    try:
                        # Use database query to check explicit access for sensitive incidents
                        from models import incident_user_access

                        access_query = db.session.query(incident_user_access).filter(
                            incident_user_access.c.incident_id == incident.id,
                            incident_user_access.c.user_id == current_user.id,
                        )
                        if access_query.first():
                            has_access = True
                    except Exception:
                        # If there's an error accessing the relationship, deny access
                        pass
                if has_access:
                    accessible_incidents.append(incident)
        incidents = accessible_incidents
    else:
        # Non-authenticated users only see public incidents
        incidents = [i for i in incidents if i.security_level == "public"]

    # Get all users and groups for filter dropdowns
    users = User.query.all()
    groups = Group.query.all()
    return render_template(
        "incidents/list.html",
        incidents=incidents,
        filter_type="group",
        group_id=group_id,
        users=users,
        groups=groups,
    )


@incidents_bp.route("/create", methods=["GET", "POST"])
@login_required
def incidents_create():
    """Create a new incident"""
    if request.method == "POST":
        title = request.form["title"]
        summary = request.form.get("summary")
        why1 = request.form.get("why1")
        why2 = request.form.get("why2")
        why3 = request.form.get("why3")
        why4 = request.form.get("why4")
        why5 = request.form.get("why5")
        status = request.form.get("status", "open")
        security_level = request.form.get("security_level", "private")
        owner_id = request.form.get("owner_id")

        # Validate that owner is provided (required field)
        if not owner_id:
            flash("Owner is required.", "error")
            # Get all users and groups for the form
            users: List[User] = User.query.all()
            groups: List[Group] = Group.query.all()
            return render_template(
                "incidents/create.html",
                users=users,
                groups=groups,
                title=title,
                summary=summary,
                why1=why1,
                why2=why2,
                why3=why3,
                why4=why4,
                why5=why5,
                status=status,
                security_level=security_level,
            )

        incident = Incident(
            title=title,
            summary=summary,
            why1=why1,
            why2=why2,
            why3=why3,
            why4=why4,
            why5=why5,
            status=status,
            security_level=security_level,
            creator_id=current_user.id,
            owner_id=owner_id,
        )

        db.session.add(incident)
        db.session.commit()
        flash("Incident created successfully!", "success")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    # Get all users and groups for the form
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template("incidents/create.html", users=users, groups=groups)


@incidents_bp.route("/<int:incident_id>")
def incidents_detail(incident_id: int):
    """View incident details"""
    incident: Incident = Incident.query.get_or_404(incident_id)

    # Check if user has permission to view this incident based on security level
    if incident.security_level == "public":
        # Public incidents are visible to everyone
        pass
    elif incident.security_level == "private":
        # Private incidents are visible to creator, owner, and admins
        if not current_user.is_authenticated:
            flash("You must be logged in to view this incident.", "error")
            return redirect(url_for("auth.login"))
        # Check permissions for private incidents
        if (
            current_user != incident.creator
            and (incident.owner is None or current_user != incident.owner)
            and not current_user.is_admin
        ):
            flash("You do not have permission to view this incident.", "error")
            return redirect(url_for("incidents_list"))
    elif incident.security_level == "sensitive":
        # Sensitive incidents are only visible to creator, admins, and explicitly granted users
        if not current_user.is_authenticated:
            flash("You must be logged in to view this incident.", "error")
            return redirect(url_for("auth.login"))
        # Check if user is creator, admin, or has explicit access
        has_access = False
        if current_user == incident.creator or current_user.is_admin:
            has_access = True
        else:
            # For sensitive incidents, we need to check explicit access
            try:
                # Use database query to check if user has explicit access
                from models import incident_user_access

                access_query = db.session.query(incident_user_access).filter(
                    incident_user_access.c.incident_id == incident_id,
                    incident_user_access.c.user_id == current_user.id,
                )
                if access_query.first():
                    has_access = True
            except Exception:
                # If there's an error accessing the relationship, deny access
                pass

        if not has_access:
            flash("You do not have permission to view this incident.", "error")
            return redirect(url_for("incidents_list"))

    return render_template("incidents/detail.html", incident=incident)


@incidents_bp.route("/<int:incident_id>/edit", methods=["GET", "POST"])
@login_required
def incidents_edit(incident_id: int):
    """Edit an incident"""
    incident: Incident = Incident.query.get_or_404(incident_id)

    # Check permissions
    if current_user != incident.creator and not current_user.is_admin:
        flash("You do not have permission to edit this incident.", "error")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    if request.method == "POST":
        incident.title = request.form["title"]
        incident.summary = request.form.get("summary")
        incident.why1 = request.form.get("why1")
        incident.why2 = request.form.get("why2")
        incident.why3 = request.form.get("why3")
        incident.why4 = request.form.get("why4")
        incident.why5 = request.form.get("why5")
        incident.status = request.form.get("status", "open")
        incident.security_level = request.form.get("security_level", "private")
        incident.assigned_group_id = request.form.get("assigned_group_id")

        db.session.commit()
        flash("Incident updated successfully!", "success")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    # Get all users and groups for the form
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template(
        "incidents/edit.html", incident=incident, users=users, groups=groups
    )


@incidents_bp.route("/<int:incident_id>/delete", methods=["POST"])
@login_required
def incidents_delete(incident_id: int):
    """Delete an incident (only admins)"""
    incident: Incident = Incident.query.get_or_404(incident_id)

    # Check permissions
    if not current_user.is_admin:
        flash("You do not have permission to delete this incident.", "error")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    db.session.delete(incident)
    db.session.commit()
    flash("Incident deleted successfully!", "success")
    return redirect(url_for("incidents.incidents_list"))


@incidents_bp.route("/<int:incident_id>/action-items/create", methods=["GET", "POST"])
@login_required
def incidents_create_action_item(incident_id: int):
    """Create a new action item for an incident"""
    incident: Incident = Incident.query.get_or_404(incident_id)

    # Check permissions - only creator, owner, or admins can create action items
    if not (
        current_user == incident.creator
        or (incident.owner and current_user == incident.owner)
        or current_user.is_admin
    ):
        flash(
            "You do not have permission to create action items for this incident.",
            "error",
        )
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    if request.method == "POST":
        title = request.form["title"]
        summary = request.form.get("summary")
        tracking_link = request.form.get("tracking_link")
        assigned_user_id = request.form["assigned_user_id"]
        status = request.form.get("status", "open")

        action_item = ActionItem(
            title=title,
            summary=summary,
            tracking_link=tracking_link,
            status=status,
            incident_id=incident.id,
            assigned_user_id=assigned_user_id,
        )

        db.session.add(action_item)
        db.session.commit()
        flash("Action item created successfully!", "success")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    # Get all users for the form
    users: List[User] = User.query.all()
    return render_template(
        "incidents/create_action_item.html", incident=incident, users=users
    )


@incidents_bp.route(
    "/<int:incident_id>/action-items/<int:action_item_id>/edit", methods=["GET", "POST"]
)
@login_required
def incidents_edit_action_item(incident_id: int, action_item_id: int):
    """Edit an action item for an incident"""
    incident: Incident = Incident.query.get_or_404(incident_id)
    action_item: ActionItem = ActionItem.query.get_or_404(action_item_id)

    # Check permissions - only creator, owner, or admins can edit action items
    if not (
        current_user == incident.creator
        or (incident.owner and current_user == incident.owner)
        or current_user.is_admin
    ):
        flash(
            "You do not have permission to edit action items for this incident.",
            "error",
        )
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    # Check if the action item belongs to this incident
    if action_item.incident_id != incident.id:
        flash("Action item does not belong to this incident.", "error")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    if request.method == "POST":
        action_item.title = request.form["title"]
        action_item.summary = request.form.get("summary")
        action_item.tracking_link = request.form.get("tracking_link")
        action_item.status = request.form.get("status", "open")
        action_item.assigned_user_id = request.form["assigned_user_id"]

        db.session.commit()
        flash("Action item updated successfully!", "success")
        return redirect(url_for("incidents.incidents_detail", incident_id=incident.id))

    # Get all users for the form
    users: List[User] = User.query.all()
    return render_template(
        "incidents/edit_action_item.html",
        incident=incident,
        action_item=action_item,
        users=users,
    )
