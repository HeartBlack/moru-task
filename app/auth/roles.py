from functools import wraps

from flask import jsonify, request

from app.models.models import Role


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = request.current_user

        if current_user["user_type"] == Role.ADMIN:
            return fn(*args, **kwargs)
        else:
            return jsonify({"error": "Admin access required"}), 403

    return wrapper
