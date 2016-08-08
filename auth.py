from flask import Blueprint, request, jsonify
from models.User import User
from datetime import datetime, timedelta
import jwt


auth_endpoints = Blueprint('blue_page', __name__, template_folder='templates')


def _create_token(user):
    payload = {
        'sub': str(user._id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, 'Some super secret token string')
    return token.decode('unicode_escape')


@auth_endpoints.route('/auth/login', methods=['POST'])
def login():
    user = User.load(request.json['email'])
    if not user or not user.validate_password(request.json['password']):
        response = jsonify(message='Wrong Email or Password')
        response.status_code = 401
        return response
    token = _create_token(user)
    return jsonify(token=token)


@auth_endpoints.route('/auth/signup', methods=['POST'])
def signup():
    user = User(email=request.json['email'])
    user.set_password(password=request.json['password'])

    if request.json['name']:
        user.name = request.json['name']

    user.save()
    token = _create_token(user)
    return jsonify(token=token)
