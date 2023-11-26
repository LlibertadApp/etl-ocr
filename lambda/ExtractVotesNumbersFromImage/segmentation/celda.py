class Celda:
    def __init__(self, id, imagen, posicion):
        self.id = id
        self.imagen = imagen
        self.posicion = posicion  # posición es una tupla (x, y, w, h)
    
    def __repr__(self):
        return f"Celda(id={self.id}, posicion={self.posicion})"