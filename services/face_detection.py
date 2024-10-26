import cv2
import mediapipe as mp
import os
import io
import base64

# Librerias necesarias para la conexion con Google Drive
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

# Función para procesar la imagen y detectar los puntos faciales
def procesar_imagen(image_path):
   # Inicializar MediaPipe para la detección de puntos clave faciales
   mp_face_mesh = mp.solutions.face_mesh

   # Cargar la imagen
   image = cv2.imread(image_path)

   # Verificar si la imagen se cargó correctamente
   if image is None:
      return {'error': f"No se pudo cargar la imagen desde {image_path}"}

   # Para guardar dinámicamente la imagen generada
   image_dir, image_filename = os.path.split(image_path)
   image_name, image_ext = os.path.splitext(image_filename)
   
   # Nombre de la imagen con los puntos detectados
   output_filename = f'bn_{image_name}{image_ext}'
   output_path = os.path.join('./', image_dir, output_filename)

   # Reescalar la imagen y convertir la imagen de BGR a RGB
   image = cv2.resize(image, (500, 500))
   image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

   # Convertir la imagen a escala de grises y luego a BGR
   image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   image_gray_bgr = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2BGR)

   # Iniciar la detección de puntos faciales
   with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
      results = face_mesh.process(image_rgb)

      puntos_deseados = [468, 473, 133, 33, 362, 263, 55, 70, 285, 300, 4, 185, 306, 0, 17]

      if results.multi_face_landmarks:
         for face_landmarks in results.multi_face_landmarks:
               for idx, landmark in enumerate(face_landmarks.landmark):
                  if idx in puntos_deseados:
                     h, w, _ = image.shape
                     x = int(landmark.x * w)
                     y = int(landmark.y * h)

                     size = 5
                     color = (0, 0, 255)  # Rojo
                     thickness = 2

                     cv2.line(image_gray_bgr, (x - size, y - size), (x + size, y + size), color, thickness)
                     cv2.line(image_gray_bgr, (x - size, y + size), (x + size, y - size), color, thickness)
                     
   # ID del folder existente en Google Drive
   folder_id = '169o8cJdktKRy2PyikWv5BRyALy2DDwds'  

   # Convertir la imagen final en un buffer en memoria
   success, encoded_image = cv2.imencode('.jpg', image_gray_bgr)
   if not success:
      return {'error': 'No se pudo codificar la imagen'}
   
   # Codificar la imagen en base64
   image_base64 = base64.b64encode(encoded_image).decode('utf-8')


   # Crear un buffer de bytes a partir de la imagen codificada
   image_buffer = io.BytesIO(encoded_image.tobytes())

   # Configurar las credenciales y subir la imagen a Google Drive
   credentials = service_account.Credentials.from_service_account_file(
      './src/services/credentials.json', scopes=['https://www.googleapis.com/auth/drive']
   )
   service = build("drive", "v3", credentials=credentials)

   # Definir los metadatos del archivo
   file_metadata = {
      'name': 'bn_imagen_procesada.jpg',  # Nombre de la imagen en Google Drive
      'parents': [folder_id]  # Carpeta de destino en Google Drive
   }

   # Crear el archivo en Google Drive usando el buffer de la imagen
   media = MediaIoBaseUpload(image_buffer, mimetype='image/jpeg')

   # Subir el archivo
   file = service.files().create(body=file_metadata, media_body=media).execute()

   # Hacer la imagen pública
   permission = {
      'type': 'anyone',
      'role': 'reader'
   }
   service.permissions().create(fileId=file['id'], body=permission).execute()

   # Obtener el enlace de la imagen subida
   file_url = f"https://drive.google.com/uc?id={file['id']}"

   # Listar los archivos dentro de la carpeta para ver el resultado
   results = service.files().list(q=f"'{folder_id}' in parents", fields="files(name)").execute()
   items = results.get('files', [])
   print(f"Archivos dentro de la carpeta: {items}")

   # Retornar los detalles del archivo subido
   return {'success': True, 'image_base64': image_base64, 'file_url': file_url}

