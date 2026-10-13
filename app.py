import os
from flask import Flask
from config import Config
from models import db
from routes.main_routes import main_bp

def create_app(config_class=Config):
    """Fábrica de la aplicación Flask (Application Factory Pattern)."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que exista la carpeta 'instance' para la base de datos SQLite
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)

    # Registrar Blueprints (Rutas modulares)
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == '__main__':
    print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
