from datetime import datetime
from models import db

class Notificacion(db.Model):
    """
    Entidad Notificacion: Mensajes del sistema hacia los clientes y personal
    (confirmaciones, cancelaciones, avisos de reasignación).
    """
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    leida = db.Column(db.Boolean, default=False)

    # Relación POO
    usuario = db.relationship('Usuario', back_populates='notificaciones')

    def marcar_leida(self):
        """Marca el mensaje como leído por el usuario."""
        self.leida = True

    def __repr__(self):
        return f"<Notificacion Usuario: {self.usuario_id} | Leída: {self.leida}>"
