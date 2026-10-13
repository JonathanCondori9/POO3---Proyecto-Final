from models import db

class Veterinario(db.Model):
    """
    Entidad Veterinario: Representa al staff médico profesional de la clínica.
    Posee una especialidad médica y una matrícula profesional habilitante.
    """
    __tablename__ = 'veterinarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False, index=True)
    especialidad = db.Column(db.String(100), nullable=False)  # 'Clínica General', 'Cirugía', 'Ecografía', etc.
    telefono = db.Column(db.String(30), nullable=True)
    correo = db.Column(db.String(120), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones POO
    turnos = db.relationship('Turno', back_populates='veterinario')

    @property
    def nombre_completo(self):
        return f"Dr/a. {self.nombre} {self.apellido}"

    def __repr__(self):
        return f"<Veterinario {self.nombre_completo} - {self.especialidad} (Mat: {self.matricula})>"
