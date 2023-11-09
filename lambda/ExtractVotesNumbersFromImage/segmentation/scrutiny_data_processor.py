class ScrutinyDataProcessor:
    def __init__(self, json_data, file_name, mapeo_codigos_a_indices, imagenes_celdas_extraidas):
        self.json_data = json_data
        self.file_name = file_name
        self.mapeo_codigos_a_indices = mapeo_codigos_a_indices
        self.imagenes_celdas_extraidas = imagenes_celdas_extraidas

    def extract_info(self):
        resultados_info = {}

        # Procesar la información de los partidos
        for partido in self.json_data["partidos"]:
            codigo_partido = partido["code"]
            votos_partido = partido["votos"]
            if codigo_partido in self.mapeo_codigos_a_indices:
                indice_imagen = self.mapeo_codigos_a_indices[codigo_partido]
                imagen_buscada = self._buscar_imagen(indice_imagen)
                resultados_info[codigo_partido] = {
                    "nombre": partido["name"],
                    "codigo": codigo_partido,
                    "votos": votos_partido,
                    "imagen": imagen_buscada
                }

        # Procesar la información de votos especiales
        campos_especiales = ['nulos', 'recurridos', 'blancos', 'impugnados', 'totalVotos']
        for campo in campos_especiales:
            votos_campo = self.json_data[campo] if campo in self.json_data else None
            codigo_campo = campo[0].upper() + campo[1:]
            if codigo_campo in self.mapeo_codigos_a_indices:
                indice_imagen = self.mapeo_codigos_a_indices[codigo_campo]
                imagen_buscada = self._buscar_imagen(indice_imagen)
                resultados_info[codigo_campo] = {
                    "nombre": codigo_campo,
                    "codigo": self.mapeo_codigos_a_indices[codigo_campo],
                    "votos": votos_campo,
                    "imagen": imagen_buscada
                }

        return resultados_info

    def _buscar_imagen(self, indice_imagen):
        return next((imagen for id_celda, imagen in self.imagenes_celdas_extraidas if id_celda == indice_imagen), None)