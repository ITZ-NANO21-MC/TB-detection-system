import os
import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.cm as cm

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
        
        # Interpretación de probabilidad
        if prediction.shape[1] == 1:
            probabilidad = float(prediction[0][0])
        else:
            probabilidad = float(prediction[0][1])
        
        deteccion = probabilidad > 0.5
        
        # Generar Mapa de Calor (Grad-CAM)
        heatmap_path = None
        # Generar Mapa de Calor (Grad-CAM)
        heatmap_path = None
        # Siempre intentamos generar el heatmap para fines de depuración/visualización
        try:
            heatmap_path = self.generate_gradcam(image_path, img_array)
        except Exception as e:
            print(f"Error detallado generando Grad-CAM: {e}")

        return {
            'deteccion_tb': deteccion,
            'probabilidad_tb': probabilidad,
            'clase_predicha': 'Tuberculosis' if deteccion else 'Normal',
            'nivel_riesgo': 'alto' if probabilidad > 0.8 else ('medio' if probabilidad > 0.5 else 'bajo'),
            'heatmap_ruta': heatmap_path
        }

    def generate_gradcam(self, image_path, img_array):
        """Genera un mapa de calor Grad-CAM para la imagen dada"""
        # 1. Encontrar la última capa convolucional
        last_conv_layer_name = None
        for layer in reversed(self.model.layers):
            if 'conv' in layer.name.lower():
                last_conv_layer_name = layer.name
                break
        
        if not last_conv_layer_name:
            return None

        # 2. Crear un modelo que mapee la entrada a las activaciones de la última capa conv
        grad_model = tf.keras.models.Model(
            [self.model.inputs], [self.model.get_layer(last_conv_layer_name).output, self.model.output]
        )

        # 3. Calcular el gradiente de la clase predicha con respecto a las activaciones
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)
            if preds.shape[1] == 1:
                class_channel = preds[:, 0]
            else:
                class_channel = preds[:, 1] # Clase TB

        grads = tape.gradient(class_channel, last_conv_layer_output)

        # 4. Promediar los gradientes (Global Average Pooling)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # 5. Pesar las activaciones por los gradientes
        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # 6. Normalizar el mapa de calor
        heatmap = np.maximum(heatmap, 0)
        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap /= max_val
        
        # 7. Generar imagen del mapa de calor
        img = Image.open(image_path).convert('RGB')
        img_size = img.size
        
        # Redimensionar el heatmap a 224x224 primero para aplicar colormap
        # y luego redimensionar al tamaño original de la imagen
        heatmap = np.uint8(255 * heatmap)
        
        # Aplicar el colormap 'jet'
        jet = cm.get_cmap("jet")
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]
        
        # Convertir a imagen PIL y redimensionar al tamaño original
        jet_heatmap_img = Image.fromarray(np.uint8(jet_heatmap * 255))
        jet_heatmap_img = jet_heatmap_img.resize(img_size, Image.Resampling.LANCZOS)
        
        # Crear una imagen RGBA para la transparencia
        # Convertimos la imagen de calor a RGBA
        heatmap_rgba = jet_heatmap_img.convert("RGBA")
        
        # Hacemos los valores bajos (azules) más transparentes
        datas = heatmap_rgba.getdata()
        new_data = []
        for item in datas:
            # Si el color es muy "frío" (bajo impacto), lo hacemos transparente
            # En Jet, el azul es (0, 0, 1xx) aprox.
            # Ajustamos la transparencia basada en la intensidad del rojo
            # item[0] es R, item[1] es G, item[2] es B
            
            # Estrategia simple: Si la intensidad roja es baja y azul alta, transparencia total
            if item[0] < 50 and item[2] > 100:
                 new_data.append((item[0], item[1], item[2], 0))
            else:
                 new_data.append((item[0], item[1], item[2], 180)) # Transparencia parcial
        
        heatmap_rgba.putdata(new_data)
        
        # Guardar heatmap
        heatmap_filename = f"heatmap_{os.path.basename(image_path)}"
        # Asegurar formato PNG para transparencia
        if not heatmap_filename.lower().endswith('.png'):
            heatmap_filename = os.path.splitext(heatmap_filename)[0] + '.png'
            
        heatmap_full_path = os.path.join(os.path.dirname(image_path), heatmap_filename)
        heatmap_rgba.save(heatmap_full_path, "PNG")
        
        return heatmap_filename
