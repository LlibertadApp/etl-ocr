from tabla import Tabla


class TelegramaBallotage:
    def __init__(self, img, binarizada):
        self.img = img
        self.binarizada = binarizada
        self.tabla_grande = self.crear_tabla(0)
        self.tabla_intermedia = self.crear_tabla(2)
        self.tabla_pequena = self.crear_tabla(3)

    def crear_tabla(self, indice):
        tabla = Tabla(self.binarizada, indice)
        return tabla

    def alinear_telegrama(self):
        # Aquí iría la lógica para alinear el telegrama
        self.alineado = True

    def capturar_tablas(self, template):
        if self.alineado and template.coordinates:
            # Aquí iría la lógica para capturar las tablas utilizando las coordenadas del template
            pass

    def obtener_celdas(self, coordenadas):
        # Aquí iría la lógica para obtener las celdas de las tablas según las coordenadas dadas
        pass