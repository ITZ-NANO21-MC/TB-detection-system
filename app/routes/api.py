import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Paciente, Estudio, ResultadoIA, Diagnostico, ModeloIA, User, Institucion
from app.services.ai_service import TBInference
from config import config

api_bp = Blueprint('api', __name__)

# Instancia global del servicio de IA
# Usamos la ruta del modelo especificada en la configuración
inference_service = TBInference(config['default'].MODEL_PATH)
inference_service.load_model()

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config['default'].ALLOWED_EXTENSIONS

@api_bp.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Actualiza la información del médico"""
    try:
        data = request.form
        nombre = data.get('nombre_completo')
        email = data.get('email')
        especialidad = data.get('especialidad')
        
        if not nombre or not email:
            return jsonify({'error': 'El nombre y el email son obligatorios'}), 400
            
        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            return jsonify({'error': 'El correo electrónico ya está en uso por otro médico'}), 400
        
        current_user.nombre_completo = nombre
        current_user.email = email
        current_user.especialidad = especialidad
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Perfil actualizado correctamente',
            'user': {
                'nombre_completo': current_user.nombre_completo,
                'email': current_user.email,
                'especialidad': current_user.especialidad
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/predict', methods=['POST'])
@login_required
def predict():
    """Endpoint para predicción de IA"""
    if 'image' not in request.files:
        return jsonify({'error': 'No se encontró la imagen'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if file and allowed_file(file.filename):
        # Datos del paciente
        nombre_paciente = request.form.get('nombre_paciente')
        numero_expediente = request.form.get('expediente')
        edad = request.form.get('edad')
        genero = request.form.get('genero')
        prioridad = request.form.get('prioridad', 'rutina')
        notas_clinicas = request.form.get('notas_clinicas', '')
        
        if not nombre_paciente or not numero_expediente:
            return jsonify({'error': 'Faltan datos obligatorios (Nombre y Expediente)'}), 400

        # Guardar archivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = config['default'].UPLOAD_FOLDER
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        
        # 1. Crear o actualizar paciente
        paciente = Paciente.query.filter_by(numero_expediente=numero_expediente).first()
        if not paciente:
            paciente = Paciente(
                institucion_id=current_user.institucion_id,
                nombre_completo=nombre_paciente, 
                numero_expediente=numero_expediente,
                genero=genero,
                historial_medico={'edad': edad, 'notas': notas_clinicas}
            )
            db.session.add(paciente)
            db.session.flush()

        # 2. Realizar inferencia
        results = inference_service.predict(filepath)
        
        # 3. Guardar Estudio
        new_study = Estudio(
            paciente_id=paciente.id,
            institucion_id=current_user.institucion_id,
            ruta_almacenamiento=unique_filename,
            prioridad=prioridad,
            notas_clinicas=notas_clinicas,
            estado='completado'
        )
        db.session.add(new_study)
        db.session.flush()

        # 4. Guardar Resultado IA
        modelo = ModeloIA.query.filter_by(es_activo=True).first()
        if not modelo:
            modelo = ModeloIA(nombre='TB_Detection_CNN', version='1.0.0', es_activo=True)
            db.session.add(modelo)
            db.session.flush()

        resultado_ia = ResultadoIA(
            estudio_id=new_study.id,
            probabilidad_tb=results['probabilidad_tb'],
            deteccion_tb=results['deteccion_tb'],
            nivel_riesgo=results['nivel_riesgo'],
            hallazgos_detectados={'general': results['clase_predicha']},
            mapa_calor_ruta=results.get('heatmap_ruta'),
            version_modelo=modelo.version,
            confianza_modelo=0.95 # Simulado
        )
        db.session.add(resultado_ia)
        db.session.flush()

        # 5. Crear diagnóstico inicial de IA
        diagnostico = Diagnostico(
            estudio_id=new_study.id,
            resultado_ia_id=resultado_ia.id,
            diagnostico_final=results['clase_predicha'],
            concordancia_ia=True,
            notas_medico='Análisis automático realizado con éxito'
        )
        db.session.add(diagnostico)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'study_id': new_study.id,
            'results': results
        })

    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@api_bp.route('/api/studies')
@login_required
def get_studies():
    """Obtiene todos los estudios realizados"""
    studies = Estudio.query.order_by(Estudio.fecha_estudio.desc()).all()
    results = []
    
    for s in studies:
        # Intentar obtener el diagnóstico final
        diag = s.diagnosticos[0].diagnostico_final if s.diagnosticos else 'Pendiente'
        
        results.append({
            'id': s.id,
            'fecha': s.fecha_estudio.isoformat(),
            'paciente': s.paciente.nombre_completo,
            'expediente': s.paciente.numero_expediente,
            'diagnostico': diag,
            'confianza': s.resultado_ia.probabilidad_tb if s.resultado_ia else 0,
            'prioridad': s.prioridad
        })
        
    return jsonify({'studies': results})

@api_bp.route('/api/study/<study_id>')
@login_required
def get_study_detail(study_id):
    """Obtiene detalles de un estudio específico"""
    study = Estudio.query.get_or_404(study_id)
    
    return jsonify({
        'id': study.id,
        'fecha': study.fecha_estudio.strftime('%d/%m/%Y %H:%M'),
        'paciente': {
            'nombre': study.paciente.nombre_completo,
            'expediente': study.paciente.numero_expediente,
            'genero': study.paciente.genero,
            'edad': study.paciente.historial_medico.get('edad', 'N/A') if study.paciente.historial_medico else 'N/A'
        },
        'estudio': {
            'tipo': study.tipo_estudio,
            'prioridad': study.prioridad,
            'notas': study.notas_clinicas,
            'imagen_url': url_for('static', filename=f'uploads/{study.ruta_almacenamiento}')
        },
        'resultado_ia': {
            'deteccion_tb': study.resultado_ia.deteccion_tb if study.resultado_ia else None,
            'probabilidad_tb': study.resultado_ia.probabilidad_tb if study.resultado_ia else 0,
            'nivel_riesgo': study.resultado_ia.nivel_riesgo if study.resultado_ia else 'bajo',
            'version_modelo': study.resultado_ia.version_modelo if study.resultado_ia else '1.0.0',
            'confianza_modelo': study.resultado_ia.confianza_modelo if study.resultado_ia else 0.95,
            'mapa_calor_url': url_for('static', filename=f'uploads/{study.resultado_ia.mapa_calor_ruta}') if study.resultado_ia and study.resultado_ia.mapa_calor_ruta else None
        } if study.resultado_ia else None,
        'diagnostico': {
            'final': study.diagnosticos[0].diagnostico_final,
            'concordancia_ia': study.diagnosticos[0].concordancia_ia,
            'razones_desacuerdo': study.diagnosticos[0].razones_desacuerdo,
            'notas_medico': study.diagnosticos[0].notas_medico
        } if study.diagnosticos else None
    })

@api_bp.route('/api/update_diagnosis', methods=['POST'])
@login_required
def update_diagnosis():
    """Actualiza el diagnóstico médico"""
    try:
        data = request.json
        study_id = data.get('study_id')
        diagnostico_final = data.get('diagnostico_final')
        concordancia_ia = data.get('concordancia_ia')
        razones_desacuerdo = data.get('razones_desacuerdo')
        notas_medico = data.get('notas_medico')
        
        study = Estudio.query.get_or_404(study_id)
        
        if study.diagnosticos:
            diag = study.diagnosticos[0]
            diag.diagnostico_final = diagnostico_final
            diag.concordancia_ia = concordancia_ia
            diag.razones_desacuerdo = razones_desacuerdo
            diag.notas_medico = notas_medico
        else:
            # Esto no debería pasar según la lógica anterior, pero por seguridad:
            new_diag = Diagnostico(
                estudio_id=study.id,
                resultado_ia_id=study.resultado_ia.id if study.resultado_ia else None,
                diagnostico_final=diagnostico_final,
                concordancia_ia=concordancia_ia,
                razones_desacuerdo=razones_desacuerdo,
                notas_medico=notas_medico
            )
            db.session.add(new_diag)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
