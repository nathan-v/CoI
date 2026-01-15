from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Group, ActionItem
from typing import List

# Action Items blueprint
action_items_bp = Blueprint("action_items", __name__, url_prefix="/action-items")


@action_items_bp.route("/")
@login_required
def action_items_list() -> str:
    """List all open action items"""
    # Get all open action items
    action_items: List[ActionItem] = (
        ActionItem.query.filter_by(status="open")
        .order_by(ActionItem.created_at.desc())
        .all()
    )
    # Get all users and groups for filter dropdowns
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template(
        "action_items/list.html",
        action_items=action_items,
        filter_type="all_open",
        users=users,
        groups=groups,
    )


@action_items_bp.route("/user/<int:user_id>")
@login_required
def action_items_by_user(user_id: int) -> str:
    """List action items assigned to a specific user"""
    # Get all action items assigned to this user
    action_items: List[ActionItem] = (
        ActionItem.query.filter_by(assigned_user_id=user_id)
        .order_by(ActionItem.created_at.desc())
        .all()
    )
    # Get all users and groups for filter dropdowns
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template(
        "action_items/list.html",
        action_items=action_items,
        filter_type="user",
        user_id=user_id,
        users=users,
        groups=groups,
    )


@action_items_bp.route("/group/<int:group_id>")
@login_required
def action_items_by_group(group_id: int) -> str:
    """List action items for a specific group (including nested groups)"""

    # Get all groups in the hierarchy (including nested groups)
    def get_all_child_groups(group_id: int) -> List[int]:
        """Recursively get all child groups"""
        child_groups = Group.query.filter(Group.parent_groups.any(id=group_id)).all()
        all_groups = [group_id]
        for child_group in child_groups:
            all_groups.extend(get_all_child_groups(child_group.id))
        return all_groups

    # Get all groups in the hierarchy
    all_group_ids: List[int] = get_all_child_groups(group_id)

    # Get all users in these groups - using proper SQLAlchemy syntax
    users_in_groups: List[User] = User.query.filter(
        User.groups.any(Group.id.in_(all_group_ids))
    ).all()

    # Get all action items assigned to these users
    action_items: List[ActionItem] = (
        ActionItem.query.filter(
            ActionItem.assigned_user_id.in_([user.id for user in users_in_groups])
        )
        .order_by(ActionItem.created_at.desc())
        .all()
    )

    # Get all users and groups for filter dropdowns
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template(
        "action_items/list.html",
        action_items=action_items,
        filter_type="group",
        group_id=group_id,
        users=users,
        groups=groups,
    )


@action_items_bp.route("/all")
@login_required
def action_items_all() -> str:
    """List all action items (regardless of status)"""
    action_items: List[ActionItem] = ActionItem.query.order_by(
        ActionItem.created_at.desc()
    ).all()
    # Get all users and groups for filter dropdowns
    users: List[User] = User.query.all()
    groups: List[Group] = Group.query.all()
    return render_template(
        "action_items/list.html",
        action_items=action_items,
        filter_type="all",
        users=users,
        groups=groups,
    )


@action_items_bp.route("/<int:action_item_id>")
@login_required
def action_items_detail(action_item_id: int) -> str:
    """Show details of a single action item"""
    action_item: ActionItem = ActionItem.query.get_or_404(action_item_id)
    return render_template("action_items/detail.html", action_item=action_item)
