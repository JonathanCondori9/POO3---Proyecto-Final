from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorador para proteger rutas que requieren inicio de sesión."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, iniciá sesión para acceder a esta sección.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para restringir rutas exclusivamente al rol Administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Acceso restringido. Debes iniciar sesión como administrador.', 'danger')
            return redirect(url_for('auth.login'))
        if session.get('usuario_rol') != 'ADMIN':
            flash('No tienes permisos suficientes para acceder al panel de administración.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
