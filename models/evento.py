class Evento:
    def __init__(self, nombre, ubicacion, fecha, pronostico_clima="Sin datos"):
        self.__nombre = nombre
        self.__ubicacion = ubicacion
        self.__fecha = fecha
        self.__pronostico_clima = pronostico_clima

    def get_name(self):
        return self.__nombre

    def get_weather_forecast(self):
        return self.__pronostico_clima

    def __str__(self):
        return (
            f"{self.__nombre} | "
            f"{self.__ubicacion} | "
            f"{self.__fecha} | "
            f"Clima: {self.__pronostico_clima}"
        )
