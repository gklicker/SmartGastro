from flask import Blueprint, request
from api.helpers import success, created, no_content, error, pagination_meta, parse_pagination, require_roles
from repository.mysql import EventRepository
from external.weather import geocode, format_forecast

bp = Blueprint("events", __name__, url_prefix="/api/v1/eventos")
repo = EventRepository()


@bp.post("/")
@require_roles("owner", "seller")
def create():
    data = request.json or {}
    required = ("nombre", "localidad", "fecha_inicio", "fecha_fin", "creado_por")
    if not all(data.get(k) for k in required):
        return error(f"Campos requeridos: {', '.join(required)}.", 400, 4001)
    try:
        lat, lon, lugar, pais = geocode(data["localidad"])
        address = f"{lugar}, {pais}"
        forecast = format_forecast(lat, lon)
    except ValueError as e:
        return error(str(e), 422, 4221)
    except Exception:
        address = data["localidad"]
        forecast = "Sin datos de clima (error de conexión)"

    event = repo.create(
        name=data["nombre"],
        address=address,
        date_start=data["fecha_inicio"],
        date_end=data["fecha_fin"],
        created_by=data["creado_por"],
        weather_forecast=forecast,
    )
    return created(event)


@bp.get("/")
def list_all():
    page, limit = parse_pagination(request.args)
    events, total = repo.list_all(
        page=page, limit=limit,
        estado=request.args.get("estado"),
        fecha_desde=request.args.get("fecha_desde"),
        fecha_hasta=request.args.get("fecha_hasta"),
    )
    return success(events, meta=pagination_meta(page, limit, total))


@bp.get("/<int:event_id>")
def get_one(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    return success(event)


@bp.patch("/<int:event_id>")
@require_roles("owner", "seller")
def update(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    if event["status"] != "planned":
        return error("Solo se pueden editar eventos en estado 'planned'.", 422, 4222)
    return success(repo.update(event_id, request.json or {}))


@bp.patch("/<int:event_id>/iniciar")
@require_roles("owner", "seller")
def start(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    if event["status"] != "planned":
        return error("Solo se puede iniciar un evento en estado 'planned'.", 422, 4222)
    repo.update_status(event_id, "ongoing")
    return success({"id": event_id, "estado": "ongoing"})


@bp.patch("/<int:event_id>/completar")
@require_roles("owner", "seller")
def complete(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    if event["status"] != "ongoing":
        return error("Solo se puede completar un evento en estado 'ongoing'.", 422, 4222)
    repo.update_status(event_id, "completed")
    return success({"id": event_id, "estado": "completed"})


@bp.patch("/<int:event_id>/cancelar")
@require_roles("owner")
def cancel(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    if event["status"] == "completed":
        return error("No se puede cancelar un evento completado.", 422, 4223)
    data = request.json or {}
    repo.update_status(
        event_id, "cancelled",
        cancellation_reason=data.get("motivo"),
        cancellation_comment=data.get("comentario"),
    )
    return success({"id": event_id, "estado": "cancelled"})


@bp.get("/<int:event_id>/pronostico")
def forecast(event_id):
    event = repo.find_by_id(event_id)
    if not event:
        return error(f"Evento #{event_id} no encontrado.", 404, 4041)
    try:
        lat, lon, lugar, pais = geocode(event["address"].split(",")[0])
        from external.weather import get_daily_summary
        resumen = get_daily_summary(lat, lon)
        return success({
            "evento_id": event_id,
            "nombre": event["name"],
            "fecha": str(event["date_start"]),
            "pronostico": {**resumen, "fuente": "Open-Meteo API"},
        })
    except Exception as e:
        return error(f"No se pudo obtener el pronóstico: {e}", 422, 4224)
