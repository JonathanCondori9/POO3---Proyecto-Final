import os
from flask import Flask, session
from config import Config
from models import db
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.mascota_routes import mascota_bp
from routes.turno_routes import turno_bp
from routes.admin_routes import admin_bp
from routes.notificacion_routes import notificacion_bp

def create_app(config_class=Config):
    """Fábrica de la aplicación Flask (Application Factory Pattern)."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que exista la carpeta 'instance' para la base de datos SQLite
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Inicializar base de datos ORM
    db.init_app(app)

    # Crear tablas en SQLite automáticamente si aún no existen
    with app.app_context():
        import models  # Asegura que todos los modelos estén cargados
        db.create_all()

    # Inyección de contexto global (ej. contador de notificaciones pendientes para el navbar)
    @app.context_processor
    def inject_notificaciones():
        if 'usuario_id' in session:
            try:
                from models.notificacion import Notificacion
                count = Notificacion.query.filter_by(
                    usuario_id=session['usuario_id'],
                    leida=False
                ).count()
                return {'notificaciones_no_leidas_count': count}
            except Exception:
                return {'notificaciones_no_leidas_count': 0}
        return {'notificaciones_no_leidas_count': 0}

    # Registrar Blueprints (Rutas modulares)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mascota_bp)
    app.register_blueprint(turno_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacion_bp)

    return app

app = create_app()

if __name__ == '__main__':
    print("Iniciando servidor de desarrollo en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
