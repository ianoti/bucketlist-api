from flask_httpauth import HTTPTokenAuth
from flask import jsonify, g

from app.models import User
# sets the token to use Authorization header with prefix of Bearer
token_auth = HTTPTokenAuth("Bearer")


@token_auth.verify_token
def verify_token(token):
    """ verify the authentication token """
    user_id = User.token_confirm(token)
    if user_id:
        g.user = User.query.filter_by(id=user_id).first()
        return True
    return False


@token_auth.error_handler
def auth_error():
    """ return json response for unauthorised access """
    return jsonify({"message": "Access denied"}), 401
