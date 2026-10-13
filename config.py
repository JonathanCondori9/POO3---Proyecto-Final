import os

class Config:
    # Clave secreta para sesiones seguras y formularios
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-veterinaria-poo3-2026'
    
    # Ruta absoluta a la base de datos SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(BASE_DIR, "instance", "veterinaria.db")}'
    
    # Deshabilitar seguimiento de modificaciones innecesario para ahorrar memoria
    SQLALCHEMY_TRACK_MODIFICATIONS = False
