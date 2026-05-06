from flask import Blueprint, request
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import ReceiptRepository, MenuItemRepository

bp = Blueprint("tickets", __name__, url_prefix="/api/v1/tickets")
repo = ReceiptRepository()
menu_repo = MenuItemRepository()


@bp.post("/")
@require_roles("cashier", "seller")
def create():
    data = request.get_json(silent=True) or {}
    required = ("foodtruck_id", "cajero_id", "medio_pago")
    if not all(data.get(k) for k in required):
        return error(f"Campos requeridos: {', '.join(required)}.", 400, 4001)
    try:
        ticket = repo.create(
            foodtruck_id=data["foodtruck_id"],
            cashier_id=data["cajero_id"],
            payment_method=data["medio_pago"],
            event_id=data.get("evento_id"),
        )
        return created(ticket)
    except ValueError as e:
        return error(str(e), 422, 4221)


@bp.post("/<int:ticket_id>/items")
@require_roles("cashier", "seller")
def add_item(ticket_id):
    data = request.get_json(silent=True) or {}
    if not data.get("menu_item_id") or not data.get("cantidad"):
        return error("Campos requeridos: menu_item_id, cantidad.", 400, 4001)
    item = menu_repo.find_by_id(data["menu_item_id"])
    if not item:
        return error(f"Plato #{data['menu_item_id']} no encontrado.", 404, 4042)
    if not item["active"]:
        return error(f"El plato '{item['name']}' no está disponible.", 422, 4221)
    ticket = repo.add_item(ticket_id, data["menu_item_id"], int(data["cantidad"]), float(item["price"]))
    return success(ticket)


@bp.post("/<int:ticket_id>/items/batch")
@require_roles("cashier", "seller")
def add_items_batch(ticket_id):
    data = request.get_json(silent=True) or {}
    items_data = data.get("items", [])
    if not items_data:
        return error("Se requiere al menos un item en 'items'.", 400, 4001)
    items = []
    for entry in items_data:
        item = menu_repo.find_by_id(entry.get("menu_item_id"))
        if not item:
            return error(f"Plato #{entry.get('menu_item_id')} no encontrado.", 404, 4042)
        if not item["active"]:
            return error(f"El plato '{item['name']}' no está disponible.", 422, 4221)
        items.append({
            "menu_item_id": item["id"],
            "quantity": int(entry["cantidad"]),
            "unit_price": float(item["price"]),
        })
    ticket = repo.add_items_batch(ticket_id, items)
    return success(ticket)


@bp.get("/<int:ticket_id>")
def get_one(ticket_id):
    ticket = repo.find_by_id(ticket_id)
    if not ticket:
        return error(f"Ticket #{ticket_id} no encontrado.", 404, 4041)
    return success(ticket)


@bp.get("/")
@require_roles("owner", "accountant")
def list_all():
    page, limit = parse_pagination(request.args)
    tickets, total = repo.list_all(
        page=page, limit=limit,
        evento_id=request.args.get("evento_id"),
        estado=request.args.get("estado"),
        cajero_id=request.args.get("cajero_id"),
        fecha_desde=request.args.get("fecha_desde"),
        fecha_hasta=request.args.get("fecha_hasta"),
    )
    return success(tickets, meta=pagination_meta(page, limit, total))


@bp.patch("/<int:ticket_id>/cerrar")
@require_roles("cashier", "seller")
def close(ticket_id):
    try:
        ticket = repo.close(ticket_id)
        return success(ticket)
    except ValueError as e:
        return error(str(e), 422, 4221)


@bp.patch("/<int:ticket_id>/cancelar")
@require_roles("cashier", "owner")
def cancel(ticket_id):
    try:
        ticket = repo.cancel(ticket_id)
        return success(ticket)
    except ValueError as e:
        return error(str(e), 422, 4221)
