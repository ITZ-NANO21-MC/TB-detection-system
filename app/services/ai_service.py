import os
import tensorflow as tf
import numpy as np
from PIL import Image

class TBInference:
    """Clase para manejar las inferencias del modelo de IA"""
    
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.img_size = (224, 224) # Tamaño estándar para muchos modelos Pretrained
        
    def load_model(self):
        """Carga el modelo de TensorFlow/Keras"""
        if os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"Modelo cargado correctamente desde {self.model_path}")
                return True
            except Exception as e:
                print(f"Error cargando el modelo: {str(e)}")
                return False
        else:
            print(f"El archivo del modelo no existe en: {self.model_path}")
        return False

    def preprocess_image(self, image_path):
        """Preprocesa la imagen para el modelo"""
        img = Image.open(image_path).convert('RGB')
        img = img.resize(self.img_size)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def predict(self, image_path):
        """Realiza la predicción real usando el modelo cargado"""
        if self.model is None:
            if not self.load_model():
                raise Exception("El modelo no pudo ser cargado para la predicción")
        
        # Preprocesar imagen
        img_array = self.preprocess_image(image_path)
        
        # Realizar inferencia
        prediction = self.model.predict(img_array)
        
        # El modelo suele devolver [probabilidad_normal, probabilidad_tb] o similar
        # Ajustamos según el formato común de salida del modelo (Binary o Multi-class)
        if prediction.shape[1] == 1:
            # Caso binario (Sigmoid): una sola salida
            probabilidad = float(prediction[0][0])
        else:
            # Caso categórico (Softmax): elegimos la clase de TB (asumiendo que es el índice 1)
            probabilidad = float(prediction[0][1])
        
        deteccion = probabilidad > 0.5
        
        return {
            'deteccion_tb': deteccion,
            'probabilidad_tb': probabilidad,
            'clase_predicha': 'Tuberculosis' if deteccion else 'Normal',
            'nivel_riesgo': 'alto' if probabilidad > 0.8 else ('medio' if probabilidad > 0.5 else 'bajo')
        }
