from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Usuario
from routes.auth_utils import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """CU-01: Registro de nuevos usuarios (clientes)."""
    if 'usuario_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validaciones de negocio
        if not nombre or not apellido or not email or not password:
            flash('Todos los campos obligatorios deben estar completos.', 'danger')
            return render_template('auth/registro.html', nombre=nombre, apellido=apellido, email=email, telefono=telefono)

        if len(password) < 6:
            flash('La contraseña debe contener al menos 6 caracteres.', 'danger')
            return render_template('auth/registro.html', nombre=nombre, apellido=apellido, email=email, telefono=telefono)

        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/registro.html', nombre=nombre, apellido=apellido, email=email, telefono=telefono)

        # Verificar unicidad de email
        if Usuario.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado en el sistema.', 'danger')
            return render_template('auth/registro.html', nombre=nombre, apellido=apellido, email=email, telefono=telefono)

        # Crear y persistir nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            rol='CLIENTE'
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('¡Cuenta creada con éxito! Ya podés iniciar sesión con tus credenciales.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """CU-02: Inicio de sesión de clientes y administradores."""
    if 'usuario_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            # Guardar datos en la sesión
            session['usuario_id'] = usuario.id
            session['usuario_nombre'] = usuario.nombre
            session['usuario_rol'] = usuario.rol
            session['usuario_email'] = usuario.email

            flash(f'¡Bienvenido/a de nuevo, {usuario.nombre}!', 'success')
            
            # Redirección según rol
            if usuario.es_admin:
                return redirect(url_for('main.index'))  # Luego redirigirá al dashboard admin
            return redirect(url_for('mascotas.mis_mascotas'))
        else:
            flash('Credenciales inválidas. Por favor verifique correo y contraseña.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Cierre de sesión seguro."""
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """CU-03: Modificar perfil de usuario autenticado."""
    usuario = Usuario.query.get_or_404(session['usuario_id'])

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        nueva_password = request.form.get('nueva_password', '')

        if not nombre or not apellido:
            flash('Nombre y apellido no pueden quedar vacíos.', 'danger')
            return render_template('auth/perfil.html', usuario=usuario)

        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.telefono = telefono

        if nueva_password:
            if len(nueva_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
                return render_template('auth/perfil.html', usuario=usuario)
            usuario.set_password(nueva_password)

        db.session.commit()
        session['usuario_nombre'] = usuario.nombre
        flash('Datos de perfil actualizados exitosamente.', 'success')
        return redirect(url_for('auth.perfil'))

    return render_template('auth/perfil.html', usuario=usuario)
