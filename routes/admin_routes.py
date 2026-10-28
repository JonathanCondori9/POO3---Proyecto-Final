from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db
from models.turno import Turno
from models.veterinario import Veterinario
from models.usuario import Usuario
from models.mascota import Mascota
from models.tipo_turno import TipoTurno
from models.notificacion import Notificacion
from routes.auth_utils import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─────────────────────────────────────────────
# CU-11 / CU-14: Dashboard general del admin
# ─────────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    """Panel principal con métricas del día y del sistema."""
    hoy = date.today()

    # Turnos del día
    turnos_hoy = Turno.query.filter(
        db.func.date(Turno.fecha_hora) == hoy
    ).all()

    # Métricas del día
    pendientes_hoy = sum(1 for t in turnos_hoy if t.estado == Turno.ESTADO_PENDIENTE)
    atendidos_hoy  = sum(1 for t in turnos_hoy if t.estado == Turno.ESTADO_ATENDIDO)
    ausentes_hoy   = sum(1 for t in turnos_hoy if t.estado == Turno.ESTADO_AUSENTE)

    # Métricas globales del sistema
    total_usuarios    = Usuario.query.filter_by(rol='CLIENTE').count()
    total_mascotas    = Mascota.query.count()
    total_veterinarios = Veterinario.query.filter_by(activo=True).count()
    total_turnos_mes  = Turno.query.filter(
        db.extract('month', Turno.fecha_hora) == hoy.month,
        db.extract('year',  Turno.fecha_hora) == hoy.year
    ).count()

    # Próximos turnos pendientes (los 5 siguientes)
    proximos_turnos = Turno.query.filter(
        Turno.estado == Turno.ESTADO_PENDIENTE,
        Turno.fecha_hora >= datetime.now()
    ).order_by(Turno.fecha_hora.asc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        turnos_hoy=turnos_hoy,
        pendientes_hoy=pendientes_hoy,
        atendidos_hoy=atendidos_hoy,
        ausentes_hoy=ausentes_hoy,
        total_usuarios=total_usuarios,
        total_mascotas=total_mascotas,
        total_veterinarios=total_veterinarios,
        total_turnos_mes=total_turnos_mes,
        proximos_turnos=proximos_turnos,
        hoy=hoy
    )


# ─────────────────────────────────────────────
# CU-12: Agenda del día — ver y gestionar turnos
# ─────────────────────────────────────────────
@admin_bp.route('/agenda')
@admin_required
def agenda():
    """Vista de agenda: todos los turnos de una fecha seleccionada."""
    # Toma la fecha del query param o usa hoy
    fecha_str = request.args.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    # Veterinario filtrado (opcional)
    vet_id = request.args.get('vet_id', type=int)

    # Consulta base: todos los turnos del día
    query = Turno.query.filter(
        db.func.date(Turno.fecha_hora) == fecha
    )
    if vet_id:
        query = query.filter(Turno.veterinario_id == vet_id)

    turnos_dia = query.order_by(Turno.fecha_hora.asc()).all()
    veterinarios = Veterinario.query.filter_by(activo=True).order_by(Veterinario.apellido).all()

    return render_template(
        'admin/agenda.html',
        turnos_dia=turnos_dia,
        veterinarios=veterinarios,
        fecha=fecha,
        vet_id_filtro=vet_id
    )


# ─────────────────────────────────────────────
# CU-12: Marcar turno como ATENDIDO
# ─────────────────────────────────────────────
@admin_bp.route('/turno/<int:id>/atendido', methods=['POST'])
@admin_required
def marcar_atendido(id):
    """Transición de estado: PENDIENTE → ATENDIDO."""
    turno = Turno.query.get_or_404(id)

    if turno.estado != Turno.ESTADO_PENDIENTE:
        flash(f'El turno ya tiene estado "{turno.estado}" y no puede marcarse como atendido.', 'danger')
        return redirect(request.referrer or url_for('admin.agenda'))

    observaciones = request.form.get('observaciones', '').strip() or None
    turno.marcar_atendido(observaciones)
    
    noti = Notificacion(
        usuario_id=turno.usuario_id,
        mensaje=f"Tu turno para {turno.mascota.nombre} ({turno.tipo_turno.practica}) ha sido completado y atendido con éxito.",
        tipo='CONFIRMACION'
    )
    db.session.add(noti)
    db.session.commit()

    flash(
        f'✅ Turno de {turno.mascota.nombre} marcado como ATENDIDO correctamente.',
        'success'
    )
    return redirect(request.referrer or url_for('admin.agenda'))


# ─────────────────────────────────────────────
# CU-12: Marcar turno como AUSENTE
# ─────────────────────────────────────────────
@admin_bp.route('/turno/<int:id>/ausente', methods=['POST'])
@admin_required
def marcar_ausente(id):
    """Transición de estado: PENDIENTE → AUSENTE."""
    turno = Turno.query.get_or_404(id)

    if turno.estado != Turno.ESTADO_PENDIENTE:
        flash(f'El turno ya tiene estado "{turno.estado}" y no puede marcarse como ausente.', 'danger')
        return redirect(request.referrer or url_for('admin.agenda'))

    turno.marcar_ausente()
    
    noti = Notificacion(
        usuario_id=turno.usuario_id,
        mensaje=f"Aviso de inasistencia: El turno de {turno.mascota.nombre} el {turno.fecha_hora.strftime('%d/%m/%Y %H:%M hs')} fue registrado como AUSENTE.",
        tipo='INFO'
    )
    db.session.add(noti)
    db.session.commit()

    flash(
        f'⚠️ Turno de {turno.mascota.nombre} marcado como AUSENTE.',
        'info'
    )
    return redirect(request.referrer or url_for('admin.agenda'))



# ─────────────────────────────────────────────
# CU-03 / HU-09 Escenario 2: Reasignación operativa de un turno
# ─────────────────────────────────────────────
@admin_bp.route('/turno/<int:id>/reprogramar', methods=['GET', 'POST'])
@admin_required
def reprogramar_turno(id):
    """
    CU-03 / HU-09 Escenario 2: Reasignación operativa de una cita pendiente en agenda.
    Despacha una notificación prioritaria al perfil del cliente afectado.
    """
    turno = Turno.query.get_or_404(id)
    veterinarios = Veterinario.query.filter_by(activo=True).all()

    if request.method == 'POST':
        fecha_str = request.form.get('fecha', '').strip()
        hora_str = request.form.get('hora', '').strip()
        vet_id = request.form.get('veterinario_id', type=int)

        if not fecha_str or not hora_str:
            flash('Por favor ingresá la nueva fecha y hora para la reasignación.', 'danger')
            return redirect(url_for('admin.reprogramar_turno', id=turno.id))

        try:
            nueva_fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Fecha u horario inválidos.', 'danger')
            return redirect(url_for('admin.reprogramar_turno', id=turno.id))

        nuevo_vet = Veterinario.query.get(vet_id) if vet_id else turno.veterinario
        turno.reasignar(nueva_fecha_hora, nuevo_vet)

        # HU-09 Escenario 2: Notificación prioritaria al cliente afectado
        noti = Notificacion(
            usuario_id=turno.usuario_id,
            mensaje=f"Aviso de reasignación operativa: Tu turno para {turno.mascota.nombre} ({turno.tipo_turno.practica}) fue reprogramado para el {nueva_fecha_hora.strftime('%d/%m/%Y a las %H:%M hs')} con el {turno.veterinario.nombre_completo if turno.veterinario else 'veterinario de turno'}.",
            tipo='REASIGNACION'
        )
        db.session.add(noti)
        db.session.commit()

        flash(f'✅ Turno de {turno.mascota.nombre} reasignado exitosamente. Se notificó al cliente.', 'success')
        return redirect(url_for('admin.agenda', fecha=nueva_fecha_hora.strftime('%Y-%m-%d')))

    return render_template('admin/reprogramar_turno.html', turno=turno, veterinarios=veterinarios)

# ─────────────────────────────────────────────
# CU-15: Ver listado de clientes y sus mascotas
# ─────────────────────────────────────────────
@admin_bp.route('/clientes')
@admin_required
def clientes():
    """Listado de todos los clientes registrados con sus mascotas."""
    busqueda = request.args.get('q', '').strip()

    query = Usuario.query.filter_by(rol='CLIENTE')
    if busqueda:
        like = f'%{busqueda}%'
        query = query.filter(
            db.or_(
                Usuario.nombre.ilike(like),
                Usuario.apellido.ilike(like),
                Usuario.email.ilike(like)
            )
        )

    clientes_lista = query.order_by(Usuario.apellido, Usuario.nombre).all()

    return render_template(
        'admin/clientes.html',
        clientes=clientes_lista,
        busqueda=busqueda
    )


# ─────────────────────────────────────────────
# CU-16: Listado de veterinarios
# ─────────────────────────────────────────────
@admin_bp.route('/veterinarios')
@admin_required
def veterinarios():
    """ABM de veterinarios: listado completo."""
    vets = Veterinario.query.order_by(Veterinario.apellido, Veterinario.nombre).all()
    return render_template('admin/veterinarios.html', veterinarios=vets)


# ─────────────────────────────────────────────
# CU-16: Nuevo veterinario
# ─────────────────────────────────────────────
@admin_bp.route('/veterinarios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_veterinario():
    """Formulario para registrar un nuevo profesional veterinario."""
    if request.method == 'POST':
        nombre      = request.form.get('nombre', '').strip()
        apellido    = request.form.get('apellido', '').strip()
        matricula   = request.form.get('matricula', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        telefono    = request.form.get('telefono', '').strip() or None
        correo      = request.form.get('correo', '').strip() or None

        # Validaciones básicas
        if not all([nombre, apellido, matricula, especialidad]):
            flash('Completá todos los campos obligatorios.', 'danger')
            return render_template('admin/form_veterinario.html', modo='nuevo',
                                   datos=request.form)

        if Veterinario.query.filter_by(matricula=matricula).first():
            flash(f'Ya existe un veterinario con la matrícula {matricula}.', 'danger')
            return render_template('admin/form_veterinario.html', modo='nuevo',
                                   datos=request.form)

        vet = Veterinario(
            nombre=nombre,
            apellido=apellido,
            matricula=matricula,
            especialidad=especialidad,
            telefono=telefono,
            correo=correo,
            activo=True
        )
        db.session.add(vet)
        db.session.commit()

        flash(f'✅ Veterinario {vet.nombre_completo} registrado exitosamente.', 'success')
        return redirect(url_for('admin.veterinarios'))

    return render_template('admin/form_veterinario.html', modo='nuevo', datos={})


# ─────────────────────────────────────────────
# CU-16: Editar veterinario
# ─────────────────────────────────────────────
@admin_bp.route('/veterinarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_veterinario(id):
    """Formulario para modificar los datos de un veterinario existente."""
    vet = Veterinario.query.get_or_404(id)

    if request.method == 'POST':
        nombre      = request.form.get('nombre', '').strip()
        apellido    = request.form.get('apellido', '').strip()
        matricula   = request.form.get('matricula', '').strip()
        especialidad = request.form.get('especialidad', '').strip()
        telefono    = request.form.get('telefono', '').strip() or None
        correo      = request.form.get('correo', '').strip() or None

        if not all([nombre, apellido, matricula, especialidad]):
            flash('Completá todos los campos obligatorios.', 'danger')
            return render_template('admin/form_veterinario.html', modo='editar',
                                   datos=request.form, vet=vet)

        # Verificar matrícula única (excepto si es la propia)
        existente = Veterinario.query.filter_by(matricula=matricula).first()
        if existente and existente.id != vet.id:
            flash(f'Ya existe otro veterinario con la matrícula {matricula}.', 'danger')
            return render_template('admin/form_veterinario.html', modo='editar',
                                   datos=request.form, vet=vet)

        vet.nombre      = nombre
        vet.apellido    = apellido
        vet.matricula   = matricula
        vet.especialidad = especialidad
        vet.telefono    = telefono
        vet.correo      = correo
        db.session.commit()

        flash(f'✅ Datos de {vet.nombre_completo} actualizados correctamente.', 'success')
        return redirect(url_for('admin.veterinarios'))

    return render_template('admin/form_veterinario.html', modo='editar',
                           datos=vet, vet=vet)


# ─────────────────────────────────────────────
# CU-16: Activar / Desactivar veterinario
# ─────────────────────────────────────────────
@admin_bp.route('/veterinarios/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_veterinario(id):
    """Cambia el estado activo/inactivo de un veterinario."""
    vet = Veterinario.query.get_or_404(id)
    vet.activo = not vet.activo
    db.session.commit()

    estado = 'activado' if vet.activo else 'desactivado'
    flash(f'✅ Veterinario {vet.nombre_completo} {estado} correctamente.', 'success')
    return redirect(url_for('admin.veterinarios'))
