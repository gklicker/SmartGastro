from flask import Blueprint, request
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import MenuItemRepository, IngredientRepository

bp = Blueprint("menu", __name__, url_prefix="/api/v1/menu")
repo = MenuItemRepository()
ing_repo = IngredientRepository()


@bp.post("/")
@require_roles("owner", "cook")
def create():
    data = request.get_json(silent=True) or {}
    if not data.get("nombre") or data.get("precio") is None:
        return error("Campos requeridos: nombre, precio.", 400, 4001)
    if float(data["precio"]) < 0:
        return error("El precio no puede ser negativo.", 422, 4221)
    item = repo.create(data["nombre"], float(data["precio"]), data.get("descripcion", ""))
    return created(item)


@bp.get("/")
def list_all():
    page, limit = parse_pagination(request.args)
    precio_max = request.args.get("precio_max")
    items, total = repo.list_active(
        page=page, limit=limit,
        nombre=request.args.get("nombre"),
        precio_max=float(precio_max) if precio_max else None,
    )
    return success(items, meta=pagination_meta(page, limit, total))


@bp.get("/<int:item_id>")
def get_one(item_id):
    item = repo.find_by_id(item_id)
    if not item:
        return error(f"Plato #{item_id} no encontrado.", 404, 4041)
    return success(item)


@bp.patch("/<int:item_id>")
@require_roles("owner", "cook")
def update(item_id):
    if not repo.find_by_id(item_id):
        return error(f"Plato #{item_id} no encontrado.", 404, 4041)
    data = request.get_json(silent=True) or {}
    if "precio" in data and float(data["precio"]) < 0:
        return error("El precio no puede ser negativo.", 422, 4221)
    return success(repo.update(item_id, data))


@bp.post("/<int:item_id>/ingredientes")
@require_roles("owner", "cook")
def add_ingredient(item_id):
    if not repo.find_by_id(item_id):
        return error(f"Plato #{item_id} no encontrado.", 404, 4041)
    data = request.get_json(silent=True) or {}
    if not data.get("ingrediente_id") or not data.get("cantidad"):
        return error("Campos requeridos: ingrediente_id, cantidad.", 400, 4001)
    if not ing_repo.find_by_id(data["ingrediente_id"]):
        return error(f"Ingrediente #{data['ingrediente_id']} no encontrado.", 404, 4042)
    item = repo.add_ingredient(item_id, data["ingrediente_id"], float(data["cantidad"]))
    return success(item)


@bp.delete("/<int:item_id>/ingredientes/<int:ing_id>")
@require_roles("owner", "cook")
def remove_ingredient(item_id, ing_id):
    repo.remove_ingredient(item_id, ing_id)
    return no_content()


@bp.patch("/<int:item_id>/desactivar")
@require_roles("owner")
def deactivate(item_id):
    if not repo.find_by_id(item_id):
        return error(f"Plato #{item_id} no encontrado.", 404, 4041)
    repo.deactivate(item_id)
    return success({"id": item_id, "activo": False})


@bp.delete("/<int:item_id>")
@require_roles("owner")
def delete(item_id):
    if not repo.find_by_id(item_id):
        return error(f"Plato #{item_id} no encontrado.", 404, 4041)
    try:
        repo.delete(item_id)
        return no_content()
    except ValueError as e:
        return error(str(e), 409, 4091)
