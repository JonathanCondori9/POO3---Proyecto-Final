from flask_sqlalchemy import SQLAlchemy

# Instancia global del ORM SQLAlchemy
db = SQLAlchemy()

# Importar todos los modelos para que SQLAlchemy los reconozca en el esquema
from models.usuario import Usuario
from models.mascota import Mascota
from models.veterinario import Veterinario
from models.tipo_turno import TipoTurno
from models.turno import Turno
from models.notificacion import Notificacion

__all__ = [
    'db',
    'Usuario',
    'Mascota',
    'Veterinario',
    'TipoTurno',
    'Turno',
    'Notificacion'
]
