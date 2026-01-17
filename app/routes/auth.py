from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Institucion

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos médicos"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        especialidad = request.form.get('especialidad')

        # Validaciones básicas
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400

        # Obtener institución por defecto
        institucion = Institucion.query.first()

        new_user = User(
            username=username,
            email=email,
            nombre_completo=nombre,
            especialidad=especialidad,
            institucion_id=institucion.id
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuario registrado correctamente'})

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'message': 'Sesión iniciada'})

        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Cierre de sesión"""
    logout_user()
    return redirect(url_for('main.index'))
