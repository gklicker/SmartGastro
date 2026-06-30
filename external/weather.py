import requests
from datetime import date, datetime

BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode(location_name):
    """Convierte un nombre de localidad a coordenadas (lat, lon).
    Lanza ValueError si no se encuentra la localidad."""
    response = requests.get(
        GEOCODING_URL,
        params={"name": location_name, "count": 1, "language": "es"},
        timeout=5,
    )
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise ValueError(f"No se encontró la localidad: '{location_name}'")
    result = results[0]
    return result["latitude"], result["longitude"], result["name"], result.get("country", "")


def get_forecast(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation",
        "forecast_days": 1,
    }

    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    return response.json()


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
    data = response.json()
    daily = data.get("daily", {})
    if not daily.get("time"):
        raise ValueError("No hay pronóstico disponible para esa fecha.")

    result = {
        "date": target_date.isoformat(),
        "rain_mm": daily.get("precipitation_sum", [0])[0] or 0,
        "rain_probability": daily.get("precipitation_probability_max", [0])[0] or 0,
        "temp_max": daily.get("temperature_2m_max", [None])[0],
        "temp_min": daily.get("temperature_2m_min", [None])[0],
        "time": target_time,
    }

    if target_time:
        target_hour = datetime.combine(
            target_date, datetime.strptime(target_time, "%H:%M").time()
        ).replace(minute=0)
        hour_key = target_hour.isoformat(timespec="minutes")
        hourly = data.get("hourly", {})
        if hour_key in hourly.get("time", []):
            index = hourly["time"].index(hour_key)
            result["hour_temp"] = hourly.get("temperature_2m", [None])[index]
            result["hour_rain_mm"] = hourly.get("precipitation", [0])[index] or 0
            result["hour_rain_probability"] = (
                hourly.get("precipitation_probability", [0])[index] or 0
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

    hourly = data.get("hourly", {})
    precipitaciones = hourly.get("precipitation", [])
    temperaturas = hourly.get("temperature_2m", [])

    total_lluvia = sum(precipitaciones)
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
    except requests.RequestException:
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
