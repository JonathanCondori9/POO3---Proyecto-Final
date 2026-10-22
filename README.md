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
│   ├── app.py                      
│   ├── config.py                   
│   ├── requirements.txt            
│   ├── seed.py                     
│   ├── README.md                   
│   └── .gitignore                  
│
├── 🧠 M: MODELOS (POO / Base de Datos)
│   └── models/
│       ├── __init__.py             
│       ├── usuario.py              
│       ├── mascota.py              
│       ├── veterinario.py          
│       ├── tipo_turno.py           
│       ├── turno.py                
│       └── notificacion.py         
│
├── 🎮 C: CONTROLADORES (Rutas y Lógica de Negocio)
│   └── routes/
│       ├── __init__.py             
│       ├── auth_utils.py           
│       ├── main_routes.py          
│       ├── auth_routes.py          
│       └── mascota_routes.py       
│
├── 👁️ V: VISTAS (Plantillas HTML con Jinja2)
│   └── templates/
│       ├── base.html               
│       ├── index.html              
│       ├── auth/
│       │   ├── login.html          
│       │   ├── registro.html       
│       │   └── perfil.html         
│       └── mascotas/
│           ├── mis_mascotas.html   
│           └── form_mascota.html   
│
├── 🎨 RECURSOS ESTÁTICOS
│   └── static/
│       └── css/
│           └── styles.css          
│
├── 🗄️ BASE DE DATOS LOCAL
│   └── instance/
│       └── veterinaria.db          
│
└── 📄 DOCUMENTACIÓN DE ENTREGA
    ├── DER.md                      
    ├── Diagrama_DER.png            
    └── TP_Final_Etapa_1_Actualizado.docx 
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
