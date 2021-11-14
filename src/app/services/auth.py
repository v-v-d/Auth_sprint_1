from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from .storages import refresh_list_storage, black_list_storage


def auth_user(user):
    access_token = create_access_token(identity=user.login)

    refresh_token = black_list_storage.check(user.login)

    if not refresh_token:
        refresh_token = create_refresh_token(identity=user.login)
        refresh_list_storage.add(user.login, refresh_token)

    return jsonify(
        access_token=access_token, refresh_token=refresh_token, msg="Token created"
    )


def black_list(token):
    black_list_storage.add(token)
    return jsonify(msg="Token add black list")


def check_black_list(token):
    check = black_list_storage.check(token)
    return check
