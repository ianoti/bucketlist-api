from flask_httpauth import HTTPTokenAuth
from flask import jsonify, g

from app.models import User

token_auth = HTTPTokenAuth("Bearer")


@token_auth.verify_token
def verify_token(token):
    user_id = User.token_confirm(token)
    if user_id:
        g.user = User.query.filter_by(id=user_id).first()
        return True
    return False


@token_auth.error_handler
def auth_error():
    return jsonify({"message": "Access denied"}), 401
