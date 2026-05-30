from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import UserRepository

bp = Blueprint("users", __name__, url_prefix="/api/v1/usuarios")
repo = UserRepository()


@bp.post("/")
@require_roles("owner")
def create():
    data = request.json or {}
    required = ("login", "password", "full_name", "role")
    if not all(data.get(k) for k in required):
        return error("Campos requeridos: login, password, full_name, role.", 400, 4001)
    try:
        user = repo.create(data["login"], data["password"], data["full_name"], data["role"])
        user.pop("password_hash", None)
        return created(user)
    except ValueError as e:
        return error(str(e), 409, 4091)


@bp.get("/")
@require_roles("owner", "accountant")
def list_all():
    page, limit = parse_pagination(request.args)
    users, total = repo.list_all(
        page=page, limit=limit,
        role=request.args.get("rol"),
        active=request.args.get("activo"),
        nombre=request.args.get("nombre"),
    )
    for u in users:
        u.pop("password_hash", None)
    return success(users, meta=pagination_meta(page, limit, total))


@bp.get("/<int:user_id>")
@require_roles("owner", "accountant")
def get_one(user_id):
    user = repo.find_by_id(user_id)
    if not user:
        return error(f"Usuario #{user_id} no encontrado.", 404, 4041)
    user.pop("password_hash", None)
    return success(user)


@bp.patch("/<int:user_id>")
@require_roles("owner")
def update(user_id):
    if not repo.find_by_id(user_id):
        return error(f"Usuario #{user_id} no encontrado.", 404, 4041)
    data = request.json or {}
    try:
        user = repo.update(user_id, data)
        user.pop("password_hash", None)
        return success(user)
    except ValueError as e:
        return error(str(e), 422, 4221)


@bp.patch("/<int:user_id>/desactivar")
@require_roles("owner")
def deactivate(user_id):
    if not repo.find_by_id(user_id):
        return error(f"Usuario #{user_id} no encontrado.", 404, 4041)
    repo.deactivate(user_id)
    return success({"id": user_id, "activo": False})


@bp.delete("/<int:user_id>")
@require_roles("owner")
def delete(user_id):
    if not repo.find_by_id(user_id):
        return error(f"Usuario #{user_id} no encontrado.", 404, 4041)
    try:
        repo.delete(user_id)
        return no_content()
    except ValueError as e:
        return error(str(e), 409, 4091)
