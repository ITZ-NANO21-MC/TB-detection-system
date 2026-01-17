from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class Institucion(db.Model):
    """Modelo para instituciones médicas"""
    __tablename__ = 'instituciones'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pacientes = db.relationship('Paciente', backref='institucion', lazy=True)
    estudios = db.relationship('Estudio', backref='institucion', lazy=True)
    usuarios = db.relationship('User', backref='institucion', lazy=True)

class User(db.Model, UserMixin):
    """Modelo para médicos/usuarios del sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    especialidad = db.Column(db.String(100))
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paciente(db.Model):
    """Modelo para pacientes"""
    __tablename__ = 'pacientes'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id'), nullable=False)
    numero_expediente = db.Column(db.String(50), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    genero = db.Column(db.String(10))
    historial_medico = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    estudios = db.relationship('Estudio', backref='paciente', lazy=True)

class Estudio(db.Model):
    """Modelo para estudios médicos"""
    __tablename__ = 'estudios'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    paciente_id = db.Column(db.String(36), db.ForeignKey('pacientes.id'), nullable=False)
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id'), nullable=False)
    tipo_estudio = db.Column(db.String(100), nullable=False, default='Radiografía Torácica')
    fecha_estudio = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    ruta_almacenamiento = db.Column(db.String(500), nullable=False)
    notas_clinicas = db.Column(db.Text)
    prioridad = db.Column(db.String(20), default='rutina')
    
    # Relaciones
    resultado_ia = db.relationship('ResultadoIA', backref='estudio', uselist=False, lazy=True)
    diagnosticos = db.relationship('Diagnostico', backref='estudio', lazy=True)

class ResultadoIA(db.Model):
    """Modelo para resultados de IA"""
    __tablename__ = 'resultados_ia'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    estudio_id = db.Column(db.String(36), db.ForeignKey('estudios.id'), nullable=False, unique=True)
    probabilidad_tb = db.Column(db.Float, nullable=False)
    deteccion_tb = db.Column(db.Boolean, nullable=False)
    nivel_riesgo = db.Column(db.String(20), nullable=False)
    hallazgos_detectados = db.Column(JSON)
    mapa_calor_ruta = db.Column(db.String(500))
    confianza_modelo = db.Column(db.Float)
    version_modelo = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Diagnostico(db.Model):
    """Modelo para diagnósticos médicos"""
    __tablename__ = 'diagnosticos'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    estudio_id = db.Column(db.String(36), db.ForeignKey('estudios.id'), nullable=False)
    resultado_ia_id = db.Column(db.String(36), db.ForeignKey('resultados_ia.id'), nullable=False)
    diagnostico_final = db.Column(db.String(200), nullable=False)
    concordancia_ia = db.Column(db.Boolean, nullable=False)
    razones_desacuerdo = db.Column(db.Text)
    notas_medico = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    resultado_ia = db.relationship('ResultadoIA', backref='diagnostico', lazy=True)

class ModeloIA(db.Model):
    """Modelo para control de versiones de IA"""
    __tablename__ = 'modelos_ia'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nombre = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    arquitectura = db.Column(db.String(100))
    es_activo = db.Column(db.Boolean, default=True)
    ruta_modelo = db.Column(db.String(500))
    fecha_implementacion = db.Column(db.DateTime, default=datetime.utcnow)
    metricas = db.Column(JSON)
