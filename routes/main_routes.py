from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página de inicio del sistema de gestión de turnos veterinarios."""
    return render_template('index.html')

@main_bp.route('/perfil')
def perfil_direct():
    """Acceso directo a perfil de usuario."""
    return redirect(url_for('auth.perfil'))
