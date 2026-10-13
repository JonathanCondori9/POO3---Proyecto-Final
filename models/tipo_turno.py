from models import db

class TipoTurno(db.Model):
    """
    Entidad TipoTurno: Modela los servicios o prácticas médicas brindadas.
    Permite diferenciar turnos generales de cirugías/especialidades y configurar
    la duración del bloque horario y los días habilitados.
    """
    __tablename__ = 'tipos_turno'

    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)  # 'General', 'Particular', 'Control'
    practica = db.Column(db.String(100), nullable=False)  # 'Consulta Clínica', 'Vacunación', 'Castración', 'Ecografía'
    duracion_minutos = db.Column(db.Integer, default=30, nullable=False)  # Ej: 30 min (general), 60 min (cirugía)
    dias_habilitados = db.Column(db.String(100), default='Lunes a Viernes')  # Ej: 'Solo Martes y Jueves'
    activo = db.Column(db.Boolean, default=True)

    # Relaciones POO
    turnos = db.relationship('Turno', back_populates='tipo_turno')

    def __repr__(self):
        return f"<TipoTurno {self.practica} ({self.categoria}) - {self.duracion_minutos} min>"
