from flask import Blueprint, request
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import FoodtruckRepository

bp = Blueprint("foodtrucks", __name__, url_prefix="/api/v1/foodtrucks")
repo = FoodtruckRepository()


@bp.post("/")
@require_roles("owner")
def create():
    data = request.json or {}
    if not data.get("nombre"):
        return error("Campo requerido: nombre.", 400, 4001)
    ft = repo.create(data["nombre"], data.get("patente"), data.get("descripcion", ""))
    return created(ft)


@bp.get("/")
@require_roles("owner", "accountant")
def list_all():
    page, limit = parse_pagination(request.args)
    activo = request.args.get("activo")
    if activo is not None:
        activo = activo.lower() == "true"
    fts, total = repo.list_all(page=page, limit=limit, activo=activo, nombre=request.args.get("nombre"))
    return success(fts, meta=pagination_meta(page, limit, total))


@bp.get("/<int:ft_id>")
def get_one(ft_id):
    ft = repo.find_by_id(ft_id)
    if not ft:
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    return success(ft)


@bp.patch("/<int:ft_id>")
@require_roles("owner")
def update(ft_id):
    if not repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    return success(repo.update(ft_id, request.json or {}))


@bp.post("/<int:ft_id>/staff")
@require_roles("owner")
def add_staff(ft_id):
    data = request.json or {}
    if not data.get("usuario_id"):
        return error("Campo requerido: usuario_id.", 400, 4001)
    try:
        ft = repo.add_staff(ft_id, data["usuario_id"])
        return success(ft)
    except ValueError as e:
        return error(str(e), 409, 4091)


@bp.delete("/<int:ft_id>/staff/<int:user_id>")
@require_roles("owner")
def remove_staff(ft_id, user_id):
    repo.remove_staff(ft_id, user_id)
    return no_content()


@bp.patch("/<int:ft_id>/desactivar")
@require_roles("owner")
def deactivate(ft_id):
    if not repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    repo.deactivate(ft_id)
    return success({"id": ft_id, "activo": False})


@bp.delete("/<int:ft_id>")
@require_roles("owner")
def delete(ft_id):
    if not repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    try:
        repo.delete(ft_id)
        return no_content()
    except ValueError as e:
        return error(str(e), 409, 4091)
