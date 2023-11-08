import cv2
import numpy as np

from celda import Celda

class ImageProcessor:
    def __init__(self, img_template, img):
        self.img_template = img_template
        self.img = img
        self.aligned_image = None

    def read_and_align_images(self):
        # Alinear la imagen usando SIFT y FLANN
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(self.img_template, None)
        kp2, des2 = sift.detectAndCompute(self.img, None)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        # Almacenar todos los buenos matches según el test de Lowe
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

        if len(good_matches) > 10:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Calcular la homografía
            M, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

            # Aplicar la transformación de perspectiva
            self.aligned_image = cv2.warpPerspective(self.img, M, (self.img_template.shape[1], self.img_template.shape[0]))
            return True
        else:
            print("Not enough matches are found - {}/{}".format(len(good_matches), 10))
            return False

    def binarize_aligned_image(self, threshold=127):
        if self.aligned_image is None:
            raise ValueError("Imagen no alineada. Por favor, ejecute primero el método read_and_align_images.")
        _, binarizada = cv2.threshold(self.aligned_image, threshold, 255, cv2.THRESH_BINARY_INV)
        return binarizada
    
    def binarize_template_image(self, threshold=127):
        if self.img_template is None:
            raise ValueError("Imagen de template no cargada. Por favor, ejecute primero el método read_and_align_images.")
        _, binarizada = cv2.threshold(self.img_template, threshold, 255, cv2.THRESH_BINARY_INV)
        return binarizada
    
    def process_table_basic(self, table_recorte, min_area_celda=1000, num_columnas = 9, num_filas = 17):
        # Paso 1: Encontrar contornos de celdas en la tabla
        celdas = self.find_cells(table_recorte, min_area=min_area_celda)

        # Paso 2: Ordenar los contornos de las celdas encontrados
        self.celdas_ordenadas = sorted(celdas, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
        
        self.celdas_ordenadas = self.ordenar_celdas(self.celdas_ordenadas, num_columnas, num_filas)

        # Paso 3: Extraer el contenido de las celdas ordenadas
        celdas_extraidas = self.extract_cells(self.celdas_ordenadas, table_recorte)

        # Paso 4: Devolver las celdas ordenadas y sus contenidos extraídos
        return self.celdas_ordenadas, celdas_extraidas
         
    def extract_cells(self, cells, img):
        extracted_cells = []
        for cell in cells:
            # Extraer la ROI utilizando recorte
            x, y, w, h = cv2.boundingRect(cell)
            cropped_image = img[y:y + h, x:x + w]
            extracted_cells.append(cropped_image)
        return extracted_cells

    def find_rectangular_contours(self, img):
        # Encontrar contornos
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Encontrar contornos rectangulares
        rectangular_contours = []
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            #approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
            approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
            if len(approx) == 4:
                rectangular_contours.append(approx)
        return rectangular_contours

    def find_cells(self, table, min_area=20):
        candidates = self.find_rectangular_contours(table)
        cells = []
        for contour in candidates:
            area = cv2.contourArea(contour)
            if area > min_area:
                cells.append(contour)
        return cells

    def ordenar_celdas(self, contornos, num_columnas, num_filas):
        # Ordenar por la coordenada Y
        contornos = sorted(contornos, key=lambda c: cv2.boundingRect(c)[1])

        # Organizar los contornos en filas
        filas = []
        fila_actual = []

        y_actual = -1
        for contorno in contornos:
            x, y, w, h = cv2.boundingRect(contorno)

            # Si estamos en una nueva fila o es el primer contorno
            if y_actual == -1 or abs(y - y_actual) > h // 2:  # h//2 es una tolerancia, ajustable según sea necesario
                y_actual = y
                if fila_actual:  # Si ya había una fila en progreso, la agregamos a filas
                    filas.append(fila_actual)
                fila_actual = [contorno]
            else:
                fila_actual.append(contorno)

        # Agregar la última fila si falta
        if fila_actual:
            filas.append(fila_actual)

        # Verificar que el número de filas detectado es correcto
        if len(filas) != num_filas:
            print(f"Advertencia: se detectaron {len(filas)} filas, pero se esperaban {num_filas}.")

        # Ordenar cada fila por la coordenada X
        for i in range(len(filas)):
            filas[i] = sorted(filas[i], key=lambda c: cv2.boundingRect(c)[0])

        # Aplanar la lista de filas en una lista única de contornos ordenados
        contornos_ordenados = [contorno for fila in filas for contorno in fila]

        return contornos_ordenados
    
    def process_table(self, table_recorte, min_area_celda=1000, num_columnas=9, num_filas=17):
        # Encuentra y ordena las celdas como antes
        celdas = self.find_cells(table_recorte, min_area=min_area_celda)
        celdas_ordenadas = sorted(celdas, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
        celdas_ordenadas = self.ordenar_celdas(celdas_ordenadas, num_columnas, num_filas)
        celdas_extraidas = self.extract_cells(celdas_ordenadas, table_recorte)
        
        # Crea la lista de objetos Celda
        lista_celdas = []
        for i, (cell, img) in enumerate(zip(celdas_ordenadas, celdas_extraidas)):
            x, y, w, h = cv2.boundingRect(cell)
            celda = Celda(id=i+1, imagen=img, posicion=(x, y, w, h))
            lista_celdas.append(celda)
        
        return lista_celdas
        
    def extract_cells_by_id(self, celdas_procesadas, indices_celdas_a_extraer, tabla_grande_recorte):
        imagenes_celdas_extraidas = []
        for celda in celdas_procesadas:
            if celda.id in indices_celdas_a_extraer:
                x, y, w, h = celda.posicion
                imagen_celda = tabla_grande_recorte[y:y+h, x:x+w]
                imagenes_celdas_extraidas.append((celda.id, imagen_celda))
        return imagenes_celdas_extraidas

    def combine_cells_by_id(self, celdas_procesadas, indices_celdas_a_extraer, tabla_grande_recorte):
        # Inicializa los valores máximos y mínimos con los del primer índice
        if not indices_celdas_a_extraer:
            print("No se proporcionaron índices de celdas para extraer.")
            return None
        if not isinstance(tabla_grande_recorte, np.ndarray):
            print("El recorte de la tabla grande no es un array de NumPy.")
            return None

        if indices_celdas_a_extraer:
            first_id = indices_celdas_a_extraer[0]
            first_cell = next((celda for celda in celdas_procesadas if celda.id == first_id), None)
            if not first_cell:
                return None  # Si no se encuentra la primera celda, no se puede continuar
            x_min, y_min = first_cell.posicion[0], first_cell.posicion[1]
            x_max, y_max = x_min + first_cell.posicion[2], y_min + first_cell.posicion[3]
        else:
            return None  # Si no hay índices, no se puede continuar

        # Busca los límites de todas las celdas a extraer
        for celda in celdas_procesadas:
            if celda.id in indices_celdas_a_extraer:
                x, y, w, h = celda.posicion
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)
        
        # Ahora x_min, y_min, x_max, y_max definen el rectángulo que contiene todas las celdas
        # Extrae esa parte de la imagen
        imagen_combinada = tabla_grande_recorte[y_min:y_max, x_min:x_max]

        if not isinstance(imagen_combinada, np.ndarray):
            print("La imagen combinada no es un array de NumPy.")
            return None

        return imagen_combinada
