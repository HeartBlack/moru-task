import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request

from app.models.models import User
from config import Config


def token_required(f):
    SECRET_KEY = Config.SECRET_KEY

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["public_id"]).first()
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401
            setattr(
                request,
                "current_user",
                {
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "user_type": current_user.user_type,
                },
            )
            # if not current_user.user_type=="admin":
            #     abort(403)

        except Exception as e:
            return {"message": "Something went wrong", "data": None, "error": str(e)}, 500

        return f(*args, **kwargs)

    return decorated


def make_access_token(user):
    access_token = jwt.encode(
        {"public_id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
        Config.SECRET_KEY,
        algorithm="HS256",
    )
    return access_token
