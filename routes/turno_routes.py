from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Turno, Mascota, TipoTurno, Veterinario, Notificacion
from routes.auth_utils import login_required
from routes.agenda_service import obtener_horarios_disponibles, es_dia_habilitado

turno_bp = Blueprint('turnos', __name__, url_prefix='/turnos')

@turno_bp.route('/mis-turnos')
@login_required
def mis_turnos():
    """
    CU-10: Ver historial de turnos.
    Separa los turnos activos (PENDIENTE) del historial finalizado (ATENDIDO, AUSENTE, CANCELADO).
    """
    usuario_id = session['usuario_id']
    
    turnos_activos = Turno.query.filter_by(
        usuario_id=usuario_id,
        estado=Turno.ESTADO_PENDIENTE
    ).order_by(Turno.fecha_hora.asc()).all()

    turnos_historial = Turno.query.filter(
        Turno.usuario_id == usuario_id,
        Turno.estado != Turno.ESTADO_PENDIENTE
    ).order_by(Turno.fecha_hora.desc()).all()

    return render_template(
        'turnos/mis_turnos.html',
        turnos_activos=turnos_activos,
        turnos_historial=turnos_historial
    )


@turno_bp.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar_turno():
    """
    CU-06 / CU-07: Reservar turno general y particular.
    Valida precondiciones (tener mascota registrada), disponibilidad por servicio
    y bloquea la agenda creando el turno en estado PENDIENTE.
    """
    usuario_id = session['usuario_id']
    mascotas = Mascota.query.filter_by(usuario_id=usuario_id).all()

    # Precondición: el cliente debe tener al menos una mascota
    if not mascotas:
        flash('Para poder reservar un turno, primero debés registrar a tu mascota.', 'info')
        return redirect(url_for('mascotas.nueva_mascota'))

    tipos_turno = TipoTurno.query.filter_by(activo=True).all()
    mascota_preseleccionada_id = request.args.get('mascota_id', type=int)

    if request.method == 'POST':
        mascota_id = request.form.get('mascota_id', type=int)
        tipo_turno_id = request.form.get('tipo_turno_id', type=int)
        fecha_str = request.form.get('fecha', '').strip()
        hora_str = request.form.get('hora', '').strip()
        observaciones = request.form.get('observaciones', '').strip()

        # Validaciones básicas
        if not mascota_id or not tipo_turno_id or not fecha_str or not hora_str:
            flash('Por favor, completá todos los campos obligatorios del turno.', 'danger')
            return redirect(url_for('turnos.reservar_turno'))

        mascota = Mascota.query.filter_by(id=mascota_id, usuario_id=usuario_id).first_or_404()
        tipo_turno = TipoTurno.query.get_or_404(tipo_turno_id)

        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            fecha_hora_reserva = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('El formato de fecha u horario ingresado no es válido.', 'danger')
            return redirect(url_for('turnos.reservar_turno'))

        # Validar disponibilidad con el motor de agenda
        horarios_libres, error_agenda = obtener_horarios_disponibles(tipo_turno, fecha_obj)
        if hora_str not in horarios_libres:
            mensaje = error_agenda or "El horario seleccionado acaba de ocuparse o no está disponible."
            flash(f"No se pudo reservar: {mensaje}", 'danger')
            return redirect(url_for('turnos.reservar_turno'))

        # Asignar un veterinario disponible según la especialidad del servicio
        veterinario = None
        if "cirugía" in tipo_turno.practica.lower() or "castración" in tipo_turno.practica.lower():
            veterinario = Veterinario.query.filter(Veterinario.especialidad.ilike('%cirug%'), Veterinario.activo == True).first()
        elif "ecografía" in tipo_turno.practica.lower():
            veterinario = Veterinario.query.filter(Veterinario.especialidad.ilike('%ecograf%'), Veterinario.activo == True).first()
        
        # Si no hay especialista puntual, asignar al primer veterinario clínico activo
        if not veterinario:
            veterinario = Veterinario.query.filter_by(activo=True).first()

        # Crear el Turno en estado PENDIENTE (bloquea el cupo)
        nuevo_turno = Turno(
            usuario_id=usuario_id,
            mascota_id=mascota.id,
            veterinario_id=veterinario.id if veterinario else None,
            tipo_turno_id=tipo_turno.id,
            fecha_hora=fecha_hora_reserva,
            estado=Turno.ESTADO_PENDIENTE,
            observaciones=observaciones
        )

        db.session.add(nuevo_turno)

        # Generar notificación para el usuario
        noti = Notificacion(
            usuario_id=usuario_id,
            mensaje=f"Turno confirmado para {mascota.nombre} ({tipo_turno.practica}) el {fecha_hora_reserva.strftime('%d/%m/%Y a las %H:%M hs')}."
            , tipo='CONFIRMACION'
        )
        db.session.add(noti)
        db.session.commit()

        flash(f'¡Turno agendado con éxito para {mascota.nombre}! Te esperamos el {fecha_hora_reserva.strftime("%d/%m/%Y a las %H:%M hs")}.', 'success')
        return redirect(url_for('turnos.mis_turnos'))

    return render_template(
        'turnos/reservar.html',
        mascotas=mascotas,
        tipos_turno=tipos_turno,
        mascota_preseleccionada_id=mascota_preseleccionada_id,
        hoy=date.today().strftime("%Y-%m-%d")
    )


@turno_bp.route('/api/disponibilidad')
@login_required
def api_disponibilidad():
    """
    Endpoint JSON consumido por el selector interactivo de fechas en el frontend.
    Devuelve la lista de horarios libres para un servicio y día determinado.
    """
    tipo_turno_id = request.args.get('tipo_turno_id', type=int)
    fecha_str = request.args.get('fecha', '').strip()
    turno_actual_id = request.args.get('turno_id', type=int)

    if not tipo_turno_id or not fecha_str:
        return jsonify({'ok': False, 'error': 'Faltan parámetros de consulta.'}), 400

    tipo_turno = TipoTurno.query.get(tipo_turno_id)
    if not tipo_turno:
        return jsonify({'ok': False, 'error': 'Tipo de turno no encontrado.'}), 404

    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({'ok': False, 'error': 'Formato de fecha inválido.'}), 400

    horarios, error_msg = obtener_horarios_disponibles(tipo_turno, fecha_obj, turno_actual_id)

    if error_msg and not horarios:
        return jsonify({'ok': False, 'error': error_msg, 'horarios': []})

    return jsonify({
        'ok': True,
        'horarios': horarios,
        'duracion': tipo_turno.duracion_minutos,
        'dias_habilitados': tipo_turno.dias_habilitados
    })


@turno_bp.route('/<int:id>/cancelar', methods=['POST'])
@login_required
def cancelar_turno(id):
    """
    CU-09: Cancelación de turno por parte del cliente.
    Regla de negocio: Transiciona el estado a CANCELADO y libera inmediatamente
    el cupo horario en la agenda.
    """
    usuario_id = session['usuario_id']
    turno = Turno.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()

    if turno.estado != Turno.ESTADO_PENDIENTE:
        flash('Solo se pueden cancelar turnos que se encuentren en estado Pendiente.', 'danger')
        return redirect(url_for('turnos.mis_turnos'))

    turno.cancelar()

    noti = Notificacion(
        usuario_id=usuario_id,
        mensaje=f"Has cancelado el turno de {turno.mascota.nombre} previsto para el {turno.fecha_hora.strftime('%d/%m/%Y a las %H:%M hs')}.", tipo='CANCELACION'
    )
    db.session.add(noti)
    db.session.commit()

    flash('El turno ha sido cancelado con éxito y el horario fue liberado en el sistema.', 'info')
    return redirect(url_for('turnos.mis_turnos'))


@turno_bp.route('/<int:id>/modificar', methods=['GET', 'POST'])
@login_required
def modificar_turno(id):
    """
    CU-08: Modificar fecha y hora de un turno existente en estado PENDIENTE.
    """
    usuario_id = session['usuario_id']
    turno = Turno.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()

    if turno.estado != Turno.ESTADO_PENDIENTE:
        flash('No se puede modificar un turno que ya fue atendido o cancelado.', 'danger')
        return redirect(url_for('turnos.mis_turnos'))

    if request.method == 'POST':
        fecha_str = request.form.get('fecha', '').strip()
        hora_str = request.form.get('hora', '').strip()

        if not fecha_str or not hora_str:
            flash('Por favor seleccioná la nueva fecha y hora.', 'danger')
            return redirect(url_for('turnos.modificar_turno', id=turno.id))

        try:
            nueva_fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            nueva_fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Fecha u horario inválidos.', 'danger')
            return redirect(url_for('turnos.modificar_turno', id=turno.id))

        horarios_libres, error_msg = obtener_horarios_disponibles(turno.tipo_turno, nueva_fecha_obj, turno_actual_id=turno.id)
        if hora_str not in horarios_libres:
            flash(f"El nuevo horario no está disponible: {error_msg}", 'danger')
            return redirect(url_for('turnos.modificar_turno', id=turno.id))

        turno.reasignar(nueva_fecha_hora)

        noti = Notificacion(
            usuario_id=usuario_id,
            mensaje=f"El turno de {turno.mascota.nombre} fue reprogramado para el {nueva_fecha_hora.strftime('%d/%m/%Y a las %H:%M hs')}.", tipo='REASIGNACION'
        )
        db.session.add(noti)
        db.session.commit()

        flash('Turno reprogramado exitosamente.', 'success')
        return redirect(url_for('turnos.mis_turnos'))

    return render_template(
        'turnos/modificar.html',
        turno=turno,
        hoy=date.today().strftime("%Y-%m-%d")
    )
