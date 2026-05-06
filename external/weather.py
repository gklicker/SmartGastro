import requests

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
