from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from .storages import refresh_list_storage


def auth_user(user):
    access_token = create_access_token(identity=user.id)
    refresh_token = refresh_list_storage.check(user.id)

    if not refresh_token:
        refresh_token = create_refresh_token(identity=user.id)
        refresh_list_storage.add(user.id, refresh_token)

    ###  redis.delete() -- или занести в блок лист

    # refresh_list_storage.add(user.id, refresh_token)

    return jsonify(access_token=access_token,
                   refresh_token=refresh_token,
                   msg="Token created")
