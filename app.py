import os
from flask import Flask
from config import Config
from models import db
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.mascota_routes import mascota_bp
from routes.turno_routes import turno_bp

def create_app(config_class=Config):
    """FÃ¡brica de la aplicaciÃ³n Flask (Application Factory Pattern)."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que exista la carpeta 'instance' para la base de datos SQLite
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Inicializar base de datos ORM
    db.init_app(app)

    # Crear tablas en SQLite automÃ¡ticamente si aÃºn no existen
    with app.app_context():
        import models  # Asegura que todos los modelos estÃ©n cargados
        db.create_all()

    # Registrar Blueprints (Rutas modulares)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mascota_bp)
    app.register_blueprint(turno_bp)

    return app

app = create_app()

if __name__ == '__main__':
    print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
