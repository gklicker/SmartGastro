from models.evento import Evento
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from external.weather import format_forecast


class SaleService:
    def __init__(self, producto_repo, venta_repo, evento_repo):
        self.__producto_repo = producto_repo
        self.__venta_repo = venta_repo
        self.__evento_repo = evento_repo

    def create_event(self, nombre, ubicacion, fecha, latitud, longitud):
        pronostico = format_forecast(latitud, longitud)
        evento = Evento(nombre, ubicacion, fecha, pronostico)
        self.__evento_repo.add(evento)
        print(f"✓ Evento creado: {evento}")
        return evento

    def register_sale(self, nombre_evento, items):
        evento = self.__evento_repo.find_by_name(nombre_evento)
        if not evento:
            raise ValueError(f"Evento '{nombre_evento}' no encontrado.")

        venta = Venta(evento)

        for nombre_producto, cantidad in items:
            producto = self.__producto_repo.find_by_name(nombre_producto)
            if not producto:
                raise ValueError(f"Producto '{nombre_producto}' no encontrado.")
            producto.deduct_stock(cantidad)
            venta.add_item(DetalleVenta(producto, cantidad))

        self.__venta_repo.add(venta)
        return venta

    def show_sales(self):
        ventas = self.__venta_repo.get_all()
        if not ventas:
            print("No hay ventas registradas.")
            return
        print("\n--- Historial de ventas ---")
        for venta in ventas:
            print(venta)
