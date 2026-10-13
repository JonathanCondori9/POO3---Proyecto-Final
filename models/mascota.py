from models import db

class Mascota(db.Model):
    """
    Entidad Mascota: Representa a los pacientes animales chicos (perros y gatos).
    Cada mascota pertenece a un Usuario (dueño/cliente).
    """
    __tablename__ = 'mascotas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  # 'Perro', 'Gato', etc.
    raza = db.Column(db.String(100), default='No especificado')
    edad = db.Column(db.String(50), nullable=True)  # Ej: '2 años', '4 meses'
    observaciones = db.Column(db.Text, nullable=True)

    # Relaciones POO
    duenio = db.relationship('Usuario', back_populates='mascotas')
    turnos = db.relationship('Turno', back_populates='mascota', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Mascota {self.nombre} ({self.especie}) - Dueño ID: {self.usuario_id}>"
