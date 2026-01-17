from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal (Landing Page)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de control para médicos logueados"""
    return render_template('dashboard.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Perfil del médico"""
    return render_template('profile.html', user=current_user)

@main_bp.route('/upload')
@login_required
def upload_page():
    """Página de subida de imágenes"""
    return render_template('upload.html')

@main_bp.route('/results/<study_id>')
@login_required
def results_page(study_id):
    """Página de resultados"""
    return render_template('results.html', study_id=study_id)
