POO3 - Proyecto Final/
│
├── ⚙️ CONFIGURACIÓN Y ARRANQUE
│   ├── app.py                      # Punto de entrada / Fábrica de la aplicación (Application Factory)
│   ├── config.py                   # Configuración de SQLite (DATABASE_URI) y SECRET_KEY
│   ├── requirements.txt            # Dependencias del proyecto (Flask, SQLAlchemy, etc.)
│   ├── seed.py                     # Script para poblar la BD con datos iniciales de prueba
│   └── .gitignore                  # Evita subir a Git la base de datos local, venv y temporales
│
├── 🧠 M: MODELOS (POO / Base de Datos con SQLAlchemy)
│   └── models/
│       ├── __init__.py             # Inicializa la instancia global de SQLAlchemy (db) y exporta clases
│       ├── usuario.py              # Clase Usuario (Clientes y Admins con hashing de passwords)
│       ├── mascota.py              # Clase Mascota (Perros y gatos vinculados al dueño)
│       ├── veterinario.py          # Clase Veterinario (Matrícula y especialidades médicas)
│       ├── tipo_turno.py           # Clase TipoTurno (Cirugías, consultas, duraciones y días)
│       ├── turno.py                # Clase Turno (Ciclo de Vida: PENDIENTE, ATENDIDO, AUSENTE, CANCELADO)
│       └── notificacion.py         # Clase Notificacion (Avisos del sistema con estado de lectura)
│
├── 🎮 C: CONTROLADORES (Lógica de Negocio y Rutas de Flask)
│   └── routes/
│       ├── __init__.py             # Identifica la carpeta como paquete de Python
│       ├── auth_utils.py           # Decoradores de seguridad (@login_required, @admin_required)
│       ├── main_routes.py          # Blueprint para la portada y páginas públicas (/)
│       ├── auth_routes.py          # Blueprint para login, registro, logout y perfil (/auth/...)
│       └── mascota_routes.py       # Blueprint para listar, agregar y editar mascotas (/mascotas/...)
│
├── 👁️ V: VISTAS (Plantillas HTML con Jinja2)
│   └── templates/
│       ├── base.html               # Layout maestro (Navbar dinámica, alertas flash y footer)
│       ├── index.html              # Portada con catálogo de servicios y presentación
│       ├── auth/
│       │   ├── login.html          # Formulario de inicio de sesión con cuentas demo
│       │   ├── registro.html       # Formulario para crear una nueva cuenta de cliente
│       │   └── perfil.html         # Pantalla para consultar o modificar datos del usuario
│       └── mascotas/
│           ├── mis_mascotas.html   # Grilla interactiva de mascotas (Milo, Luna, etc.)
│           └── form_mascota.html   # Formulario para registrar o editar una mascota
│
├── 🎨 RECURSOS ESTÁTICOS
│   └── static/
│       └── css/
│           └── styles.css          # Estilos responsivos con paleta Violeta (#855ad0) y Blanco
│
├── 🗄️ BASE DE DATOS LOCAL
│   └── instance/
│       └── veterinaria.db          # Archivo físico de la base de datos SQLite con sus 6 tablas
│
└── 📄 DOCUMENTACIÓN DE ENTREGA (ETAPA 1)
    ├── DER.md                      # Diagrama Entidad-Relación y Máquina de Estados en Markdown
    ├── Diagrama_DER.png            # Imagen descargable del diagrama de datos
    ├── TP_Final_Etapa_1.docx       # Documento de entrega para la facultad
    └── TP_Final_Etapa_1_Actualizado.docx
