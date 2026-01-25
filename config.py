import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración de la aplicación Flask"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY') or 'tb-detection-secret-key-2024'
    
    # Configuración de base de datos - RUTAS MEJORADAS
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Crear directorio para base de datos si no existe
    DB_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(DB_DIR, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f"sqlite:///{os.path.join(DB_DIR, 'tb_detection.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de uploads - RUTAS MEJORADAS
    STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')
    UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
    
    # Crear directorios necesarios
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuración del modelo
    MODELS_DIR = os.path.join(BASE_DIR, 'models_TB')
    os.makedirs(MODELS_DIR, exist_ok=True)
    MODEL_PATH = os.path.join(MODELS_DIR, 'tb_model.h5')
    IMG_SIZE = (224, 224)
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    def __init__(self):
        """Verificar y crear directorios al inicializar"""
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crear todos los directorios necesarios"""
        directories = [
            self.DB_DIR,
            self.UPLOAD_FOLDER,
            self.MODELS_DIR,
            os.path.join(self.STATIC_DIR, 'css'),
            os.path.join(self.STATIC_DIR, 'js'),
            os.path.join(self.STATIC_DIR, 'images')
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directorio verificado: {directory}")
            except Exception as e:
                print(f"❌ Error creando directorio {directory}: {e}")

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}