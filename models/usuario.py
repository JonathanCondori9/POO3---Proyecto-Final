from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class Usuario(db.Model):
    """
    Entidad Usuario: Modela tanto a los Clientes como a los Administradores de la veterinaria.
    Aplica encapsulamiento seguro para el manejo de credenciales.
    """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='CLIENTE', nullable=False)  # 'CLIENTE' o 'ADMIN'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones POO
    mascotas = db.relationship('Mascota', back_populates='duenio', cascade='all, delete-orphan')
    turnos = db.relationship('Turno', back_populates='usuario', cascade='all, delete-orphan')
    notificaciones = db.relationship('Notificacion', back_populates='usuario', cascade='all, delete-orphan')

    # Métodos de negocio y encapsulamiento
    def set_password(self, password):
        """Genera un hash criptográfico de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña ingresada contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self):
        """Devuelve True si el usuario tiene rol de Administrador."""
        return self.rol.upper() == 'ADMIN'

    @property
    def nombre_completo(self):
        """Retorna el nombre y apellido completo."""
        return f"{self.nombre} {self.apellido}"

    def __repr__(self):
        return f"<Usuario {self.email} ({self.rol})>"
