from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from api.helpers import success, error
from repository.mysql import UserRepository

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
user_repo = UserRepository()


@bp.post("/login")
def login():
    data = request.json or {}
    login_val = data.get("login", "").strip()
    password = data.get("password", "")

    if not login_val or not password:
        return error("login y password son requeridos.", 400, 4001)

    user = user_repo.find_by_login(login_val)
    if not user or not user["active"]:
        return error("Usuario no encontrado o inactivo.", 401, 4011)
    if not user_repo.check_password(user, password):
        return error("Contraseña incorrecta.", 401, 4012)

    claims = {"role": user["role"], "full_name": user["full_name"]}
    access_token = create_access_token(identity=str(user["id"]), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user["id"]), additional_claims=claims)

    return success({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": user["role"],
        "full_name": user["full_name"],
    })


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    claims = get_jwt()

    user = user_repo.find_by_id(int(user_id))
    if not user or not user["active"]:
        return error("Usuario no encontrado o inactivo.", 401, 4011)

    new_claims = {"role": user["role"], "full_name": user["full_name"]}
    access_token = create_access_token(identity=user_id, additional_claims=new_claims)
    return success({"access_token": access_token})


@bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = user_repo.find_by_id(int(user_id))
    if not user or not user["active"]:
        return error("Usuario no encontrado o inactivo.", 401, 4011)
    user.pop("password_hash", None)
    return success(user)


@bp.post("/logout")
def logout():
    # JWT is stateless — client must discard both tokens
    return "", 204
