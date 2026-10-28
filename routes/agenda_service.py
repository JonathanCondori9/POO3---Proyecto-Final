from datetime import datetime, date, time, timedelta
from models import Turno, TipoTurno, Veterinario

# Mapeo de días de la semana en Python (0: Lunes, 6: Domingo)
DIAS_MAP = {
    0: 'Lunes',
    1: 'Martes',
    2: 'Miércoles',
    3: 'Jueves',
    4: 'Viernes',
    5: 'Sábado',
    6: 'Domingo'
}

def es_dia_habilitado(tipo_turno, fecha_obj):
    """
    Verifica si una fecha determinada coincide con las restricciones de días
    habilitados del tipo de turno (ej. cirugías solo martes y jueves).
    """
    dia_semana = fecha_obj.weekday()  # 0=Lunes, 6=Domingo
    
    # La veterinaria no atiende turnos programados los domingos
    if dia_semana == 6:
        return False, "Los domingos el consultorio permanece cerrado para turnos programados."

    dias_hab = tipo_turno.dias_habilitados.lower()

    if "solo martes y jueves" in dias_hab:
        if dia_semana not in [1, 3]:
            return False, "Esta práctica (Cirugía/Castración) solo se realiza los días Martes y Jueves (quirófano habilitado)."
    elif "solo miércoles y viernes" in dias_hab:
        if dia_semana not in [2, 4]:
            return False, "Esta práctica (Ecografía/Diagnóstico) solo se realiza los días Miércoles y Viernes con especialista."
    elif "lunes a viernes" in dias_hab:
        if dia_semana not in [0, 1, 2, 3, 4]:
            return False, "Esta práctica solo se realiza de Lunes a Viernes."
    elif "lunes a sábado" in dias_hab:
        if dia_semana not in [0, 1, 2, 3, 4, 5]:
            return False, "Esta práctica se atiende de Lunes a Sábados."

    return True, ""


def obtener_horarios_disponibles(tipo_turno, fecha_obj, turno_actual_id=None):
    """
    Calcula los intervalos de horarios libres para una fecha dada,
    teniendo en cuenta la duración del servicio, los turnos en estado PENDIENTE
    y el horario comercial (09:00 a 18:00).
    """
    habilitado, mensaje_error = es_dia_habilitado(tipo_turno, fecha_obj)
    if not habilitado:
        return [], mensaje_error

    # No permitir fechas pasadas
    hoy = date.today()
    if fecha_obj < hoy:
        return [], "No se pueden seleccionar fechas pasadas."

    # Horario de atención: 09:00 a 18:00
    hora_inicio = datetime.combine(fecha_obj, time(9, 0))
    hora_fin = datetime.combine(fecha_obj, time(18, 0))
    duracion = timedelta(minutes=tipo_turno.duracion_minutos)

    # Buscar turnos que bloqueen la agenda ese día (estado PENDIENTE)
    inicio_dia = datetime.combine(fecha_obj, time.min)
    fin_dia = datetime.combine(fecha_obj, time.max)

    query = Turno.query.filter(
        Turno.fecha_hora >= inicio_dia,
        Turno.fecha_hora <= fin_dia,
        Turno.estado == Turno.ESTADO_PENDIENTE
    )
    
    if turno_actual_id:
        query = query.filter(Turno.id != turno_actual_id)

    turnos_ocupados = query.all()

    # Rangos ocupados: lista de tuplas (inicio, fin)
    rangos_ocupados = []
    for t in turnos_ocupados:
        dur_t = timedelta(minutes=t.tipo_turno.duracion_minutos if t.tipo_turno else 30)
        rangos_ocupados.append((t.fecha_hora, t.fecha_hora + dur_t))

    ahora = datetime.now()
    horarios_libres = []
    slot_actual = hora_inicio

    while slot_actual + duracion <= hora_fin:
        slot_fin = slot_actual + duracion

        # Si la fecha es hoy, no permitir horarios que ya hayan pasado
        if fecha_obj == hoy and slot_actual <= ahora:
            slot_actual += duracion
            continue

        # Verificar si colisiona con algún turno ocupado
        hay_conflicto = False
        for ocup_ini, ocup_fin in rangos_ocupados:
            if not (slot_fin <= ocup_ini or slot_actual >= ocup_fin):
                hay_conflicto = True
                break

        if not hay_conflicto:
            horarios_libres.append(slot_actual.strftime("%H:%M"))

        slot_actual += duracion

    if not horarios_libres:
        return [], "No quedan horarios disponibles para la fecha seleccionada."

    return horarios_libres, ""
