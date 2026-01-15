from flask_login import current_user, login_required
from functools import wraps
from flask import flash, redirect, url_for
from typing import Callable, Any


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require admin privileges"""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            flash("Access denied. Administrator privileges required.")
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


# Re-export login_required for convenience
login_required = login_required
