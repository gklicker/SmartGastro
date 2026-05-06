from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from api.helpers import success, error
from repository.mysql import UserRepository

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
user_repo = UserRepository()


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    login_val = data.get("login", "").strip()
    password = data.get("password", "")

    if not login_val or not password:
        return error("login y password son requeridos.", 400, 4001)

    user = user_repo.find_by_login(login_val)
    if not user or not user["active"]:
        return error("Usuario no encontrado o inactivo.", 401, 4011)
    if not user_repo.check_password(user, password):
        return error("Contraseña incorrecta.", 401, 4012)

    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"], "full_name": user["full_name"]},
    )
    return success({
        "token": token,
        "rol": user["role"],
        "nombre": user["full_name"],
    })


@bp.post("/logout")
def logout():
    # JWT is stateless — client must discard the token
    return "", 204
