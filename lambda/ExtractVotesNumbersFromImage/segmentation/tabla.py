import cv2

class Tabla:
    def __init__(self, binarizada, indice):
        self.indice = indice
        self.binarizada = binarizada
        self.contorno = None
        self.recorte = None
        self.contornos = []
        self.detectar_contornos()
        self.detectar_y_extraer_contorno()

    def detectar_contornos(self):
        """
        Detecta contornos en la imagen binarizada y almacena los contornos.
        """
        contornos, _ = cv2.findContours(self.binarizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contornos = sorted(contornos, key=cv2.contourArea, reverse=True)

    def extraer_contorno(self):
        """
        Extrae y devuelve el contorno y la imagen correspondiente al índice dado.
        """
        if not self.contornos:
            raise ValueError("Primero debe ejecutar el método detectar_contornos.")
        if self.indice >= len(self.contornos):
            raise IndexError("El índice proporcionado está fuera de rango.")
        contorno = self.contornos[self.indice]
        x, y, w, h = cv2.boundingRect(contorno)
        tabla_cortada = self.binarizada[y:y+h, x:x+w]
        return tabla_cortada, contorno
    
    def detectar_y_extraer_contorno(self):
        """
        Detecta todos los contornos y extrae el especificado por 'indice'.
        """
        contornos, _ = cv2.findContours(self.binarizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos_ordenados = sorted(contornos, key=cv2.contourArea, reverse=True)

        if self.indice >= len(contornos_ordenados):
            raise IndexError("El índice proporcionado está fuera de rango.")
        
        self.contorno = contornos_ordenados[self.indice]
        x, y, w, h = cv2.boundingRect(self.contorno)
        self.recorte = self.binarizada[y:y+h, x:x+w]
    
