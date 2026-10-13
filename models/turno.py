from datetime import datetime
from models import db

class Turno(db.Model):
    """
    Entidad Turno: Modela la cita médica veterinaria.
    Implementa el Ciclo de Vida y Máquina de Estados:
    - PENDIENTE: Cupo bloqueado en la agenda, en espera de la fecha.
    - ATENDIDO: La mascota asistió y el veterinario realizó la práctica.
    - AUSENTE: Llegó la hora y el cliente no se presentó.
    - CANCELADO: La cita fue anulada y el horario queda liberado.
    """
    __tablename__ = 'turnos'

    # Constantes de estados válidos
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_ATENDIDO = 'ATENDIDO'
    ESTADO_AUSENTE = 'AUSENTE'
    ESTADO_CANCELADO = 'CANCELADO'

    ESTADOS_VALIDOS = [ESTADO_PENDIENTE, ESTADO_ATENDIDO, ESTADO_AUSENTE, ESTADO_CANCELADO]

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('veterinarios.id'), nullable=True)
    tipo_turno_id = db.Column(db.Integer, db.ForeignKey('tipos_turno.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)
    estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, nullable=False, index=True)
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones POO
    usuario = db.relationship('Usuario', back_populates='turnos')
    mascota = db.relationship('Mascota', back_populates='turnos')
    veterinario = db.relationship('Veterinario', back_populates='turnos')
    tipo_turno = db.relationship('TipoTurno', back_populates='turnos')

    # Métodos del Ciclo de Vida (Encapsulamiento POO)
    def marcar_atendido(self, observaciones=None):
        """Transición de estado: La mascota asistió y se realizó la práctica."""
        self.estado = self.ESTADO_ATENDIDO
        if observaciones:
            self.observaciones = observaciones

    def marcar_ausente(self):
        """Transición de estado: El cliente no se presentó a la cita médica."""
        self.estado = self.ESTADO_AUSENTE

    def cancelar(self):
        """Transición de estado: Cancela el turno y libera el cupo horario."""
        self.estado = self.ESTADO_CANCELADO

    def reasignar(self, nueva_fecha_hora, nuevo_veterinario=None):
        """Reasigna fecha/hora y profesional, manteniendo el estado PENDIENTE."""
        self.fecha_hora = nueva_fecha_hora
        if nuevo_veterinario:
            self.veterinario = nuevo_veterinario
        self.estado = self.ESTADO_PENDIENTE

    @property
    def bloquea_agenda(self):
        """Indica si este turno actualmente ocupa un lugar en la agenda."""
        return self.estado == self.ESTADO_PENDIENTE

    def __repr__(self):
        return f"<Turno ID: {self.id} | {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} | Estado: {self.estado}>"
