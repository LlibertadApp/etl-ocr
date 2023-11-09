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
    image_path: "", # imagen del telegrama previamente guardada en s3
    template_path: ""
}
'''
def handler(event, context):
    KEY_TEMPLATE = "templates"
    KEY_TELEGRAMA_PATH = "telegramas"
    KEY_COLUMNAS_PATH = "columnas"
    KEY_COLUMNA_PATH = "columna"
    KEY_CELDAS_PATH = "celdas"
    KEY_CELDA_PATH = "celda"
    # Aquí iría la lógica para manejar el evento y procesar la imagen
    try:
        # Obtener el id de la imagen desde el evento que activa la función
        code = event.get('code')
        if not id:
            raise ValueError("Invalid code")
        
        # Obtener el path image_path
        image_path = event.get('image_path')
        if not image_path:
            raise ValueError("Invalid image_path")
        
        # Obtener el path template_path
        template_path = event.get('template_path')
        if not template_path:
            raise ValueError("Invalid template_path")
        
        bucket = os.environ['BUCKET_OCR_IMAGES']        
        if not bucket:
            raise ValueError("Invalid environ BUCKET_OCR_IMAGES")
        
        # Obtener el objeto de S3
        s3_client = boto3.client('s3', region_name=os.environ['AWS_REGION'])
        img = get_image_from_s3(s3_client, bucket, image_path)
        if img is None:
            raise ValueError("Failed to get image from S3.")
        
        img_template = get_image_from_s3(s3_client, bucket, template_path)
        if img_template is None:
            raise ValueError("Failed to get image from S3.")
        
        # Procesar la imagen
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

        img_celdas_combinada_extraidas = processor.combine_cells_by_id(celdas_procesadas, indices_celdas_a_extraer, telegrama.tabla_grande.recorte)

        if img_celdas_combinada_extraidas is not None and isinstance(img_celdas_combinada_extraidas, np.ndarray):
            key_path_column = f'{KEY_TELEGRAMA_PATH}/{KEY_COLUMNAS_PATH}/{code}_{KEY_COLUMNA_PATH}.png'
            upload_image_to_s3(s3_client, img_celdas_combinada_extraidas, bucket, key_path_column)
        else:
            print("No se pudo obtener la imagen combinada como un array de NumPy.")
            
        img_celdas_extraidas = processor.extract_cells_by_id(celdas_procesadas, indices_celdas_a_extraer, telegrama.tabla_grande.recorte)
        
        for i, (indice, img) in enumerate(img_celdas_extraidas):
            key_path_cell = f'{KEY_TELEGRAMA_PATH}/{KEY_CELDAS_PATH}/{code}_{KEY_CELDA_PATH}_{i}.png'
            upload_image_to_s3(s3_client, img, bucket, key_path_cell)
        
        return {
            'processed': True
            'path': 'extracted-url-in-s3'
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
