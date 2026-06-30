import logging
import os
from datetime import date, datetime
from functools import lru_cache
from json import JSONDecodeError

import requests

BASE_URL = os.getenv(
    "OPEN_METEO_FORECAST_URL",
    "https://api.open-meteo.com/v1/forecast",
)
GEOCODING_URL = os.getenv(
    "OPEN_METEO_GEOCODING_URL",
    "https://geocoding-api.open-meteo.com/v1/search",
)

logger = logging.getLogger("smartgastro.weather")


def _first(values, default=0):
    """Devuelve el primer elemento de una lista o el default si está vacía/None."""
    if not values:
        return default
    head = values[0]
    return default if head is None else head


def _at(values, index, default=None):
    """Acceso seguro por índice; devuelve default si la lista no alcanza."""
    if not values or index is None or index >= len(values):
        return default
    return values[index] if values[index] is not None else default


def _safe_json(response):
    try:
        return response.json()
    except (JSONDecodeError, ValueError) as exc:
        logger.error("Open-Meteo respondió con JSON inválido: %s", exc)
        raise ValueError("El servicio climático devolvió una respuesta inválida.")


@lru_cache(maxsize=128)
def geocode(location_name):
    """Convierte un nombre de localidad a coordenadas (lat, lon).
    Resultados cacheados en memoria para reducir llamadas externas.
    Lanza ValueError si no se encuentra la localidad."""
    if not location_name or not location_name.strip():
        raise ValueError("La localidad no puede estar vacía.")
    response = requests.get(
        GEOCODING_URL,
        params={"name": location_name, "count": 1, "language": "es"},
        timeout=5,
    )
    response.raise_for_status()
    data = _safe_json(response)
    results = data.get("results") or []
    if not results:
        raise ValueError(f"No se encontró la localidad: '{location_name}'")
    result = results[0]
    try:
        return (
            float(result["latitude"]),
            float(result["longitude"]),
            result["name"],
            result.get("country", ""),
        )
    except (KeyError, TypeError, ValueError) as exc:
        logger.error("Respuesta de geocoding incompleta: %s", result)
        raise ValueError("La localidad no devolvió coordenadas válidas.") from exc


def get_forecast(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation",
        "forecast_days": 1,
    }

    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    return _safe_json(response)


def get_forecast_for_date(latitude, longitude, target_date, target_time=None):
    """Devuelve un resumen para una fecha concreta dentro del horizonte de Open-Meteo."""
    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    days_ahead = (target_date - date.today()).days
    if days_ahead < 0:
        raise ValueError("La fecha no puede estar en el pasado.")
    if days_ahead > 15:
        raise ValueError("El pronóstico está disponible hasta 16 días.")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,precipitation_probability_max"
        ),
        "hourly": "temperature_2m,precipitation,precipitation_probability",
        "timezone": "America/Argentina/Buenos_Aires",
        "start_date": target_date.isoformat(),
        "end_date": target_date.isoformat(),
    }
    response = requests.get(BASE_URL, params=params, timeout=7)
    response.raise_for_status()
    data = _safe_json(response)
    daily = data.get("daily") or {}
    if not daily.get("time"):
        raise ValueError("No hay pronóstico disponible para esa fecha.")

    result = {
        "date": target_date.isoformat(),
        "rain_mm": _first(daily.get("precipitation_sum"), 0),
        "rain_probability": _first(daily.get("precipitation_probability_max"), 0),
        "temp_max": _first(daily.get("temperature_2m_max"), None),
        "temp_min": _first(daily.get("temperature_2m_min"), None),
        "time": target_time,
    }

    if target_time:
        try:
            parsed_time = datetime.strptime(target_time, "%H:%M").time()
        except ValueError as exc:
            raise ValueError("El horario debe tener formato HH:MM.") from exc
        target_hour = datetime.combine(target_date, parsed_time).replace(minute=0)
        hour_key = target_hour.isoformat(timespec="minutes")
        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        if hour_key in times:
            index = times.index(hour_key)
            result["hour_temp"] = _at(hourly.get("temperature_2m"), index)
            result["hour_rain_mm"] = _at(hourly.get("precipitation"), index, 0)
            result["hour_rain_probability"] = _at(
                hourly.get("precipitation_probability"), index, 0
            )

    if result.get("hour_rain_probability", result["rain_probability"]) >= 50 or result.get(
        "hour_rain_mm", result["rain_mm"]
    ) > 0:
        result["status"] = "Hay riesgo de lluvia"
        result["recommendation"] = "Conviene reducir la producción y proteger la mercadería."
    else:
        result["status"] = "Condiciones favorables"
        result["recommendation"] = "El clima no exige reducir la producción prevista."
    return result


def get_daily_summary(latitude, longitude):
    data = get_forecast(latitude, longitude)

    hourly = data.get("hourly") or {}
    precipitaciones = hourly.get("precipitation") or []
    temperaturas = hourly.get("temperature_2m") or []

    total_lluvia = sum(value for value in precipitaciones if value is not None)
    temp_max = max(temperaturas) if temperaturas else None
    temp_min = min(temperaturas) if temperaturas else None

    if total_lluvia > 5:
        estado = "Lluvia intensa — no recomendado salir a feria"
    elif total_lluvia > 0:
        estado = "Lluvia leve — preparar mercadería reducida"
    else:
        estado = "Despejado — condiciones favorables"

    return {
        "estado": estado,
        "lluvia_total_mm": round(total_lluvia, 2),
        "temp_max": temp_max,
        "temp_min": temp_min,
    }


def format_forecast(latitude, longitude):
    try:
        resumen = get_daily_summary(latitude, longitude)
        return (
            f"{resumen['estado']} | "
            f"Lluvia: {resumen['lluvia_total_mm']} mm | "
            f"Temp: {resumen['temp_min']}°C - {resumen['temp_max']}°C"
        )
    except (requests.RequestException, ValueError) as exc:
        logger.warning("format_forecast falló: %s", exc)
        return "Sin datos de clima (error de conexión)"


def format_forecast_by_name(location_name):
    """Igual que format_forecast pero recibe un nombre de localidad en lugar de coordenadas."""
    try:
        lat, lon, nombre, pais = geocode(location_name)
        resumen = get_daily_summary(lat, lon)
        return (
            f"{nombre}, {pais} | "
            f"{resumen['estado']} | "
            f"Lluvia: {resumen['lluvia_total_mm']} mm | "
            f"Temp: {resumen['temp_min']}°C - {resumen['temp_max']}°C"
        )
    except ValueError as e:
        return f"Sin datos de clima ({e})"
    except requests.RequestException:
        return "Sin datos de clima (error de conexión)"
