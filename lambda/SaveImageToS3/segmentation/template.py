from tabla import Tabla


class Template:
    def __init__(self, img, binarizada):
        self.img = img
        self.binarizada = binarizada
        self.tabla_grande = self.crear_tabla(0)
        self.tabla_intermedia = self.crear_tabla(2)
        self.tabla_pequena = self.crear_tabla(3)

    def crear_tabla(self, indice):
        tabla = Tabla(self.binarizada, indice)
        return tabla

    def obtener_coordenadas(self):
        # Aquí iría la lógica para obtener las coordenadas de las celdas
        pass

    def guardar_coordenadas(self, coordenadas):
        self.coordinates = coordenadas