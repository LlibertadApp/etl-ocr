import sys
sys.path.insert(0, './vendor')
import os
import json
import boto3
import cv2
import traceback
import numpy as np
from io import BytesIO
from segmentation.image_processor import ImageProcessor
from segmentation.telegrama_ballotage import TelegramaBallotage
from segmentation.template_ballotage import TemplateBallotage

'''
{
    code: "0200700636X",
    // imagen del telegrama previamente guardada en s3
    image_path: "",
}
'''
def handler(event, context):
    KEY_TEMPLATE = "templates"
    KEY_TELEGRAMA_PATH = "imagenes_procesadas"
    KEY_COLUMNAS_PATH = "votos_columna"
    KEY_CELDAS_PATH = "votos_celdas"
    KEY_CELDA_PATH = "celda"

    try:
        # Obtener el path template_path
        template_path = os.environ['TELEGRAMA_TEMPLATE_TO_USE']
        if not template_path:
            raise ValueError("Invalid envar TELEGRAMA_TEMPLATE_TO_USE")
        
        bucket = os.environ['BUCKET_IMAGES']        
        if not bucket:
            raise ValueError("Invalid envar BUCKET_IMAGES")

        # Obtener el id de la imagen desde el evento que activa la función
        code = event.get('code')
        if not code:
            raise ValueError("Invalid code")
        
        # Obtener el path image_path
        image_path = event.get('image_path')
        if not image_path:
            raise ValueError("Invalid image_path")
        
        # Obtener el objeto de S3
        s3_client = boto3.client('s3', region_name=os.environ['REGION'])
        img = get_image_from_s3(s3_client, bucket, image_path)
        if img is None:
            raise ValueError("Failed to get image from S3.")
        
        # procesa la imagen usando el template
        img_template = read_image_from_path(template_path)
        processor = ImageProcessor(img_template, img)
        is_align = processor.read_and_align_images()
        aligned_binarizada = processor.binarize_aligned_image()
        template_binarizada = processor.binarize_template_image()

        # Crear instancias de Telegrama o Template con la imagen binarizada
        telegrama = TelegramaBallotage(processor.aligned_image, aligned_binarizada)
        template = TemplateBallotage(processor.img_template, template_binarizada)

        # Procesa la tabla y recibe una lista de objetos Celda
        celdas_procesadas = processor.process_table(template.tabla_grande.recorte)

        # Lista de índices de las celdas que quieres extraer
        indices_celdas_a_extraer = [30, 34, 36, 38, 40, 42, 44]

        # Imagen recortada que sera examinada por OCRs
        img_celdas_combinada_extraidas = processor.combine_cells_by_id(celdas_procesadas, indices_celdas_a_extraer, telegrama.tabla_grande.recorte)
        if img_celdas_combinada_extraidas is not None and isinstance(img_celdas_combinada_extraidas, np.ndarray):
            key_path_column = f'{KEY_TELEGRAMA_PATH}/{KEY_COLUMNAS_PATH}/{code}.png'
            upload_image_to_s3(s3_client, img_celdas_combinada_extraidas, bucket, key_path_column)
        else:
            print("No se pudo obtener la imagen combinada como un array de NumPy.")

        # Imagenes de las celdas separadas usadas por el LLM
        cells_images = []
        img_celdas_extraidas = processor.extract_cells_by_id(celdas_procesadas, indices_celdas_a_extraer, telegrama.tabla_grande.recorte)
        for i, (indice, img) in enumerate(img_celdas_extraidas):
            key_path_cell = f'{KEY_TELEGRAMA_PATH}/{KEY_CELDAS_PATH}/{code}_{KEY_CELDA_PATH}_{i}.png'
            upload_image_to_s3(s3_client, img, bucket, key_path_cell)
            cells_images.append(key_path_cell)
        
        return {
            'processed': True,
            'image': f'{KEY_TELEGRAMA_PATH}/{KEY_COLUMNAS_PATH}/{code}.png',
            'cells': cells_images
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        error_trace = traceback.format_exc()
        return {
            'processed': False,
            'error': str(e),
            'traceback': error_trace
        }

def upload_image_to_s3(s3_client, image_array, bucket, key):
    # Asegurarse de que image_array es un array de NumPy y no None
    if image_array is None:
        raise ValueError("The image_array is None")

    # Verificar que image_array tenga la estructura de datos correcta
    if not isinstance(image_array, np.ndarray):
        raise TypeError("image_array must be a numpy.ndarray")

    # Verificar que image_array no esté vacío
    if image_array.size == 0:
        raise ValueError("The image_array is empty")

    # Convertir la imagen a un objeto BytesIO    
    is_success, buffer = cv2.imencode(".png", image_array)
    if not is_success:
        raise Exception("Could not convert image to bytes. Encoding failed.")
    
    byte_io = BytesIO(buffer)

    # Subir la imagen al bucket de S3
    s3_client.put_object(Bucket=bucket, Key=key, Body=byte_io.getvalue(), ACL='public-read')

def get_image_from_s3(s3_client, bucket, key):
    """
    Obtener una imagen de un bucket S3 y convertirla a una imagen de OpenCV.

    :param s3_client: Cliente de S3.
    :param bucket: Nombre del bucket de S3.
    :param key: Clave del objeto en S3.
    :return: Imagen como un array de OpenCV.
    """
    try:
        # Obtener el objeto de S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        
        # Leer el contenido del objeto como un byte stream
        byte_stream = BytesIO(response['Body'].read())
        
        # Convertir el byte stream en un array de NumPy para OpenCV
        file_bytes = np.asarray(byte_stream.getbuffer(), dtype=np.uint8)
        
        # Leer la imagen desde el array de bytes como una imagen en escala de grises
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        return img
    except Exception as e:
        print(f"Error getting image from S3: {str(e)}")
        return None


def read_image_from_path(file_path):
    try:
        with open(file_path, "rb") as image_file:
            image_content = image_file.read()
        bytes_io = BytesIO(image_content)
        file_bytes = np.asarray(bytes_io.getbuffer(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        return img
    except Exception as e:
        # Handle exceptions, e.g., file not found, permissions, etc.
        print(f"Error reading image: {e}")
        return None