# Modelo de Datos y Ciclo de Vida del Turno - Veterinaria de Animales Chicos

## 1. Ciclo de Vida del Turno (Estados)

Un turno no solo existe, sino que va cambiando de condición a lo largo del tiempo:

* **Pendiente (u Ocupado):** El cliente ya reservó el horario. El sistema bloquea la agenda para que ningún otro usuario pueda elegir ese mismo día y hora. El turno se queda esperando a que llegue el día de la cita.
* **Atendido (Confirmado / Atendido):** El día del turno, la mascota asiste a la veterinaria y el médico realiza la práctica (castración, ecografía, consulta, etc.).
* **Ausente:** Llegó la hora del turno y el cliente no se presentó. El sistema lo marca así para llevar estadísticas de cumplimiento.
* **Cancelado:** El cliente o el administrador anularon la cita antes de tiempo. En ese instante, **el horario vuelve a quedar libre y disponible** en el sistema para otra persona.

### Diagrama de Estados
```mermaid
stateDiagram-v2
    [*] --> Pendiente : Cliente reserva / Admin asigna
    Pendiente --> Atendido : Mascota asiste y se realiza la práctica
    Pendiente --> Ausente : Llega la hora y no se presenta
    Pendiente --> Cancelado : Cliente o Admin anula la cita (libera cupo)
    Pendiente --> Pendiente : Reasignación (cambio de fecha/hora)
    Atendido --> [*]
    Ausente --> [*]
    Cancelado --> [*]
```

---

## 2. Diagrama Entidad-Relación (DER)

```mermaid
erDiagram
    USUARIO ||--o{ MASCOTA : "posee"
    USUARIO ||--o{ TURNO : "solicita / administra"
    USUARIO ||--o{ NOTIFICACION : "recibe"
    MASCOTA ||--o{ TURNO : "es paciente de"
    VETERINARIO ||--o{ TURNO : "atiende"
    TIPO_TURNO ||--o{ TURNO : "clasifica"

    USUARIO {
        int id PK
        string nombre
        string apellido
        string email
        string telefono
        string password
        string rol "CLIENTE o ADMIN"
    }

    MASCOTA {
        int id PK
        int usuario_id FK
        string nombre
        string especie "Perro, Gato"
        string raza
    }

    VETERINARIO {
        int id PK
        string nombre
        string apellido
        string matricula
        string especialidad "Clínica General, Cirugía, Ecografía, Análisis"
    }

    TIPO_TURNO {
        int id PK
        string categoria "General, Particular, Control"
        string practica "Vacunación, Castración, Extracción de sangre, Ecografía"
        int duracion_minutos
        string dias_habilitados "Ej: Lunes a Viernes, Solo Martes"
    }

    TURNO {
        int id PK
        int usuario_id FK
        int mascota_id FK
        int veterinario_id FK
        int tipo_turno_id FK
        datetime fecha_hora
        string estado "PENDIENTE, ATENDIDO, AUSENTE, CANCELADO"
        string observaciones
    }

    NOTIFICACION {
        int id PK
        int usuario_id FK
        string mensaje
        datetime fecha_envio
        boolean leida
    }
```
