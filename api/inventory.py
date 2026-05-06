from flask import Blueprint, request
from api.helpers import success, error, require_roles
from repository.mysql import FoodtruckRepository, IngredientRepository

bp = Blueprint("inventory", __name__, url_prefix="/api/v1/foodtrucks")
ft_repo = FoodtruckRepository()
ing_repo = IngredientRepository()


@bp.get("/<int:ft_id>/inventario")
def get_stock(ft_id):
    if not ft_repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    alerta = request.args.get("alerta", "").lower() == "true"
    stock = ft_repo.get_stock(ft_id, alerta_only=alerta)
    return success({"foodtruck_id": ft_id, "stock": stock})


@bp.post("/<int:ft_id>/inventario")
@require_roles("owner", "cook")
def add_stock(ft_id):
    if not ft_repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    data = request.get_json(silent=True) or {}
    if not data.get("ingrediente_id") or not data.get("cantidad"):
        return error("Campos requeridos: ingrediente_id, cantidad.", 400, 4001)
    if not ing_repo.find_by_id(data["ingrediente_id"]):
        return error(f"Ingrediente #{data['ingrediente_id']} no encontrado.", 404, 4042)
    if float(data["cantidad"]) <= 0:
        return error("La cantidad debe ser mayor a cero.", 422, 4221)
    row = ft_repo.add_stock(ft_id, data["ingrediente_id"], float(data["cantidad"]))
    return success(row)


@bp.get("/<int:ft_id>/inventario/alertas")
def get_alerts(ft_id):
    if not ft_repo.find_by_id(ft_id):
        return error(f"Foodtruck #{ft_id} no encontrado.", 404, 4041)
    alerts = ft_repo.get_stock(ft_id, alerta_only=True)
    return success({"foodtruck_id": ft_id, "alertas": alerts})
