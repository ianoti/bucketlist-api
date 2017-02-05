from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth, MultiAuth
from flask import jsonify, g

from app.models import User

token_auth = HTTPTokenAuth("Bearer")
passw_auth = HTTPBasicAuth()
multi_auth = MultiAuth(passw_auth, token_auth)


@token_auth.verify_token
def verify_token(token):
    user_id = User.token_confirm(token)
    if user_id:
        g.user = User.query.filter_by(id=user_id).first()
        return True
    return False


@passw_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    g.user = user
    return True


@token_auth.error_handler
@passw_auth.error_handler
def auth_error():
    return jsonify({"message": "Access denied"}), 401
