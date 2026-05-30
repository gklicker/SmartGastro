from flask import Blueprint, request
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import IngredientRepository

bp = Blueprint("ingredients", __name__, url_prefix="/api/v1/ingredientes")
repo = IngredientRepository()


@bp.post("/")
@require_roles("owner", "cook")
def create():
    data = request.json or {}
    if not data.get("nombre") or not data.get("unidad"):
        return error("Campos requeridos: nombre, unidad.", 400, 4001)
    ing = repo.create(data["nombre"], data["unidad"], data.get("stock_minimo_alerta", 0))
    return created(ing)


@bp.get("/")
def list_all():
    page, limit = parse_pagination(request.args)
    items, total = repo.list_all(
        page=page, limit=limit,
        nombre=request.args.get("nombre"),
        unit=request.args.get("unidad"),
    )
    return success(items, meta=pagination_meta(page, limit, total))


@bp.get("/<int:ing_id>")
def get_one(ing_id):
    ing = repo.find_by_id(ing_id)
    if not ing:
        return error(f"Ingrediente #{ing_id} no encontrado.", 404, 4041)
    return success(ing)


@bp.patch("/<int:ing_id>")
@require_roles("owner", "cook")
def update(ing_id):
    if not repo.find_by_id(ing_id):
        return error(f"Ingrediente #{ing_id} no encontrado.", 404, 4041)
    ing = repo.update(ing_id, request.json or {})
    return success(ing)


@bp.delete("/<int:ing_id>")
@require_roles("owner")
def delete(ing_id):
    if not repo.find_by_id(ing_id):
        return error(f"Ingrediente #{ing_id} no encontrado.", 404, 4041)
    try:
        repo.delete(ing_id)
        return no_content()
    except ValueError as e:
        return error(str(e), 409, 4091)
