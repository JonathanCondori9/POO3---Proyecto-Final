from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models import db
from models.notificacion import Notificacion
from routes.auth_utils import login_required

notificacion_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')

@notificacion_bp.route('/')
@login_required
def centro():
    """
    HU-09: Centro de Notificaciones.
    Visualiza el listado de alertas pendientes y el historial de notificaciones pasadas.
    Escenario 4: Si no hay mensajes nuevos, muestra aviso informativo claro.
    """
    usuario_id = session['usuario_id']

    notificaciones_nuevas = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        leida=False
    ).order_by(Notificacion.fecha_envio.desc()).all()

    notificaciones_historial = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        leida=True
    ).order_by(Notificacion.fecha_envio.desc()).limit(30).all()

    return render_template(
        'notificaciones/centro.html',
        notificaciones_nuevas=notificaciones_nuevas,
        notificaciones_historial=notificaciones_historial
    )


@notificacion_bp.route('/<int:id>/leer', methods=['POST'])
@login_required
def marcar_leida(id):
    """
    HU-09 Escenario 3: Marcar una notificación individual como leída.
    Actualiza el estado de lectura y disminuye el contador del navbar.
    """
    usuario_id = session['usuario_id']
    noti = Notificacion.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()

    noti.marcar_leida()
    db.session.commit()

    flash('Notificación marcada como leída.', 'info')
    return redirect(request.referrer or url_for('notificaciones.centro'))


@notificacion_bp.route('/marcar-todas-leidas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    """
    HU-09 Escenario 3: Marcar todas las notificaciones pendientes como leídas.
    """
    usuario_id = session['usuario_id']

    total_actualizadas = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        leida=False
    ).update({'leida': True})

    db.session.commit()

    if total_actualizadas > 0:
        flash(f'Se marcaron {total_actualizadas} notificaciones como leídas.', 'success')
    else:
        flash('No tenías notificaciones pendientes para marcar.', 'info')

    return redirect(url_for('notificaciones.centro'))


@notificacion_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Permite al usuario descartar una notificación del historial."""
    usuario_id = session['usuario_id']
    noti = Notificacion.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()

    db.session.delete(noti)
    db.session.commit()

    flash('Notificación eliminada de tu bandeja.', 'info')
    return redirect(request.referrer or url_for('notificaciones.centro'))
