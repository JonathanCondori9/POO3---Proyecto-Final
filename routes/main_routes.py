from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página de inicio del sistema de gestión de turnos veterinarios."""
    return render_template('index.html')
