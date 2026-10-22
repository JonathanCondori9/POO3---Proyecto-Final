# 🐾 VetTurnos - Sistema de Gestión de Turnos para Veterinarias de Animales Chicos

> **Proyecto Final - Programación Orientada a Objetos 3 (POO3)**  
> Sistema web integral para la administración, reserva y seguimiento clínico de turnos veterinarios para perros y gatos.

---

## 🚀 Tecnologías y Arquitectura

El sistema implementa el patrón arquitectónico **MVC / MVT (Modelo - Vista - Controlador)** con renderizado del lado del servidor (SSR):

* **Backend:** Python 3 + [Flask](https://flask.palletsprojects.com/) (ruteo modular mediante Blueprints).
* **Persistencia / ORM:** SQLite con [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) (modelado 100% orientado a objetos).
* **Seguridad:** Cifrado criptográfico de contraseñas con [Werkzeug](https://werkzeug.palletsprojects.com/) y control de acceso por roles (`CLIENTE` y `ADMIN`) mediante decoradores personalizados.
* **Frontend:** HTML5 semántico + CSS3 estructurado (paleta violeta `#855ad0` y blanco), renderizado dinámico con plantillas [Jinja2](https://jinja.palletsprojects.com/).

---

## 📁 Estructura del Proyecto

```text
POO3 - Proyecto Final/
│
├── ⚙️ CONFIGURACIÓN Y ARRANQUE
│   ├── app.py                      # Fábrica de la aplicación (Application Factory Pattern)
│   ├── config.py                   # Configuración de SQLite (DATABASE_URI) y SECRET_KEY
│   ├── requirements.txt            # Dependencias del proyecto (Flask, SQLAlchemy, etc.)
│   ├── seed.py                     # Script para poblar la BD con datos iniciales de prueba
│   ├── README.md                   # Documentación general del repositorio
│   └── .gitignore                  # Exclusión de venv, base de datos local y temporales
│
├── 🧠 M: MODELOS (POO / Base de Datos)
│   └── models/
│       ├── __init__.py             # Instancia global de SQLAlchemy (db) y exportación de modelos
│       ├── usuario.py              # Clase Usuario (Clientes y Administradores con hashing seguro)
│       ├── mascota.py              # Clase Mascota (Perros y gatos vinculados al dueño)
│       ├── veterinario.py          # Clase Veterinario (Matrícula y especialidades clínicas)
│       ├── tipo_turno.py           # Clase TipoTurno (Cirugías, consultas, duraciones y días)
│       ├── turno.py                # Clase Turno (Ciclo de Vida: PENDIENTE, ATENDIDO, AUSENTE, CANCELADO)
│       └── notificacion.py         # Clase Notificacion (Avisos del sistema con estado de lectura)
│
├── 🎮 C: CONTROLADORES (Rutas y Lógica de Negocio)
│   └── routes/
│       ├── __init__.py             # Paquete de rutas
│       ├── auth_utils.py           # Decoradores de seguridad (@login_required, @admin_required)
│       ├── main_routes.py          # Blueprint para portada y páginas públicas (/)
│       ├── auth_routes.py          # Blueprint para login, registro, logout y perfil (/auth/...)
│       └── mascota_routes.py       # Blueprint para listar, agregar y editar mascotas (/mascotas/...)
│
├── 👁️ V: VISTAS (Plantillas HTML con Jinja2)
│   └── templates/
│       ├── base.html               # Layout maestro (Navbar dinámica, alertas flash y footer)
│       ├── index.html              # Portada del consultorio y catálogo de servicios
│       ├── auth/
│       │   ├── login.html          # Formulario de inicio de sesión
│       │   ├── registro.html       # Formulario para registro de nuevos clientes
│       │   └── perfil.html         # Actualización de datos personales y contraseña
│       └── mascotas/
│           ├── mis_mascotas.html   # Grilla de mascotas registradas por el cliente
│           └── form_mascota.html   # Formulario de alta y edición de mascotas
│
├── 🎨 RECURSOS ESTÁTICOS
│   └── static/
│       └── css/
│           └── styles.css          # Estilos responsivos con paleta Violeta (#855ad0) y Blanco
│
├── 🗄️ BASE DE DATOS LOCAL
│   └── instance/
│       └── veterinaria.db          # Archivo físico SQLite con las 6 tablas generadas
│
└── 📄 DOCUMENTACIÓN DE ENTREGA
    ├── DER.md                      # Diagrama Entidad-Relación y Máquina de Estados
    ├── Diagrama_DER.png            # Imagen del DER
    └── TP_Final_Etapa_1_Actualizado.docx # Documento de entrega formal para la cátedra
```

---

## 🔄 Ciclo de Vida del Turno (Máquina de Estados)

En el sistema, la entidad `Turno` atraviesa 4 estados bien definidos que impactan en la agenda y el historial médico:

1. **`PENDIENTE` (u Ocupado):** El cliente reservó la cita. El sistema bloquea automáticamente la agenda para que ningún otro usuario pueda elegir ese mismo día y horario.
2. **`ATENDIDO`:** El paciente asiste a la veterinaria y el médico efectúa la práctica (consulta, castración, ecografía, vacuna). Queda asentado en el historial clínico.
3. **`AUSENTE`:** Llegó la fecha/hora y el cliente no se presentó. Permite llevar estadísticas de inasistencias y cumplimiento.
4. **`CANCELADO`:** El cliente o la administración anulan la cita antes de tiempo. **El cupo horario vuelve a liberarse inmediatamente** para otros usuarios.

---

## 🛠️ Instalación y Puesta en Marcha Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/JonathanCondori9/POO3---Proyecto-Final.git
cd POO3---Proyecto-Final
```

### 2. Crear y activar el entorno virtual
* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Cargar datos semilla de prueba (Seed Data)
Pobla la base de datos SQLite con usuarios, mascotas, veterinarios y turnos de ejemplo:
```bash
python seed.py
```

### 5. Iniciar el servidor de desarrollo
```bash
python app.py

* `CU-14` Reasignar turno
* `CU-15` Ver datos del cliente / mascota
* `CU-16` Gestionar veterinarios
