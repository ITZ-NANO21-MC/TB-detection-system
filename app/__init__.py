import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from app.models import db, User, Institucion, ModeloIA
from config import config

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Registrar Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    # Manejadores de errores globales
    @app.errorhandler(413)
    def too_large(e):
        from flask import jsonify
        return jsonify({'error': 'El archivo es demasiado grande (máximo 16MB)'}), 413

    @app.errorhandler(500)
    def internal_error(e):
        from flask import jsonify
        return jsonify({'error': 'Error interno del servidor'}), 500

    # Crear tablas si no existen (opcional, mejor usar migraciones en prod)
    with app.app_context():
        db.create_all()
        # Semilla básica de instituciones si está vacía
        if Institucion.query.count() == 0:
            inst = Institucion(nombre='Hospital Central', direccion='Av. Salud 123')
            db.session.add(inst)
            db.session.commit()

    return app
