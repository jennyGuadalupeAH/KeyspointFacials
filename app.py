from flask import Flask, request, jsonify, render_template
from services.face_detection import procesar_imagen
import os
from flask_cors import CORS

app = Flask(__name__)

# Permitir todas las solicitudes CORS
CORS(app)

@app.route('/')
def index():
   # Usar render_template en lugar de send_static_file
   return render_template('index.html')

@app.route('/get_key_facials', methods=['POST'])
def detectar_Puntos_Faciales():

   # Cargar la imagen
   IMAGE_PATH = './src/static/images/'  # Esto se cambiará para guardar la imagen recibida del front

   # Validar la existencia de la imagen
   archivo = request.files['archivo']
   if archivo.filename == '':
      return jsonify({'error': 'No se cargó ninguna imagen'})     

   if archivo:
      image_path = os.path.join(IMAGE_PATH, archivo.filename)
      archivo.save(image_path)

      # Llamar a la función para procesar la imagen pasando como parametro la ruta de nuestra imagen
      resultado = procesar_imagen(image_path)
      
      # Responder con la ruta de la imagen procesada
      return jsonify(resultado)

if __name__ == '__main__':
   app.run(debug=True)