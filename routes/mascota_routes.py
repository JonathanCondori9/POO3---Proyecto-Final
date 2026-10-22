from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Mascota
from routes.auth_utils import login_required

mascota_bp = Blueprint('mascotas', __name__, url_prefix='/mascotas')

@mascota_bp.route('/')
@login_required
def mis_mascotas():
    """CU-04: Visualización del listado de mascotas registradas por el cliente."""
    usuario_id = session['usuario_id']
    mascotas = Mascota.query.filter_by(usuario_id=usuario_id).all()
    return render_template('mascotas/mis_mascotas.html', mascotas=mascotas)


@mascota_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_mascota():
    """CU-04: Alta de una nueva mascota (perro o gato)."""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        especie = request.form.get('especie', '').strip()
        raza = request.form.get('raza', '').strip() or 'No especificado'
        edad = request.form.get('edad', '').strip() or 'No especificado'
        observaciones = request.form.get('observaciones', '').strip()

        if not nombre or not especie:
            flash('El nombre y la especie son obligatorios.', 'danger')
            return render_template('mascotas/form_mascota.html', titulo='Agregar Mascota', accion='Crear')

        nueva = Mascota(
            usuario_id=session['usuario_id'],
            nombre=nombre,
            especie=especie,
            raza=raza,
            edad=edad,
            observaciones=observaciones
        )

        db.session.add(nueva)
        db.session.commit()

        flash(f'¡{nombre} ha sido registrado/a con éxito en tu perfil!', 'success')
        return redirect(url_for('mascotas.mis_mascotas'))

    return render_template('mascotas/form_mascota.html', titulo='Agregar Mascota', accion='Crear', mascota=None)


@mascota_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_mascota(id):
    """CU-04: Modificación de los datos de una mascota existente."""
    mascota = Mascota.query.get_or_404(id)

    # Validar que la mascota pertenezca al usuario en sesión
    if mascota.usuario_id != session['usuario_id']:
        flash('No tienes autorización para editar esta mascota.', 'danger')
        return redirect(url_for('mascotas.mis_mascotas'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        especie = request.form.get('especie', '').strip()
        raza = request.form.get('raza', '').strip() or 'No especificado'
        edad = request.form.get('edad', '').strip() or 'No especificado'
        observaciones = request.form.get('observaciones', '').strip()

        if not nombre or not especie:
            flash('El nombre y la especie son obligatorios.', 'danger')
            return render_template('mascotas/form_mascota.html', titulo='Editar Mascota', accion='Guardar', mascota=mascota)

        mascota.nombre = nombre
        mascota.especie = especie
        mascota.raza = raza
        mascota.edad = edad
        mascota.observaciones = observaciones

        db.session.commit()
        flash(f'Datos de {mascota.nombre} actualizados correctamente.', 'success')
        return redirect(url_for('mascotas.mis_mascotas'))

    return render_template('mascotas/form_mascota.html', titulo='Editar Mascota', accion='Guardar', mascota=mascota)
