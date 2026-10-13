"""
Script de Datos Semilla (seed.py)
Puebla la base de datos SQLite con datos iniciales para desarrollo y pruebas del sistema veterinario:
- 1 Usuario Administrador y 1 Cliente de prueba
- Mascotas asociadas al cliente (perro y gato)
- Veterinarios con sus especialidades y matrículas
- Catálogo de Tipos de Turnos (generales, cirugías, ecografías, controles)
- Turnos de ejemplo reflejando los 4 estados del Ciclo de Vida: PENDIENTE, ATENDIDO, AUSENTE, CANCELADO
"""

from datetime import datetime, timedelta
from app import create_app
from models import db, Usuario, Mascota, Veterinario, TipoTurno, Turno, Notificacion

app = create_app()

def poblar_base_de_datos():
    with app.app_context():
        print("Limpiando datos existentes en la base de datos...")
        db.drop_all()
        db.create_all()

        print("1. Creando Usuarios...")
        # Administrador de la veterinaria
        admin = Usuario(
            nombre="Laura",
            apellido="Fernández",
            email="admin@veterinaria.com",
            telefono="11-4567-8901",
            rol="ADMIN"
        )
        admin.set_password("admin123")

        # Cliente de prueba
        cliente = Usuario(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@gmail.com",
            telefono="11-9876-5432",
            rol="CLIENTE"
        )
        cliente.set_password("cliente123")

        db.session.add_all([admin, cliente])
        db.session.commit()

        print("2. Registrando Mascotas para el cliente...")
        perro = Mascota(
            usuario_id=cliente.id,
            nombre="Milo",
            especie="Perro",
            raza="Golden Retriever",
            edad="3 años",
            observaciones="Alérgico a picaduras de pulgas."
        )
        gato = Mascota(
            usuario_id=cliente.id,
            nombre="Luna",
            especie="Gato",
            raza="Siamés",
            edad="1 año",
            observaciones="Plan de vacunación al día."
        )

        db.session.add_all([perro, gato])
        db.session.commit()

        print("3. Creando Staff Veterinario...")
        vet1 = Veterinario(
            nombre="Carlos",
            apellido="Gómez",
            matricula="MN-8421",
            especialidad="Clínica General",
            telefono="11-2233-4455",
            correo="carlos.gomez@vet.com",
            activo=True
        )
        vet2 = Veterinario(
            nombre="Valeria",
            apellido="Méndez",
            matricula="MN-9104",
            especialidad="Cirugía y Castraciones",
            telefono="11-3344-5566",
            correo="valeria.mendez@vet.com",
            activo=True
        )
        vet3 = Veterinario(
            nombre="Martín",
            apellido="Rossi",
            matricula="MN-7532",
            especialidad="Ecografía y Diagnóstico",
            telefono="11-4455-6677",
            correo="martin.rossi@vet.com",
            activo=True
        )

        db.session.add_all([vet1, vet2, vet3])
        db.session.commit()

        print("4. Configurando Tipos de Turno y Prácticas Médicas...")
        # Consultas de rutina
        tt_consulta = TipoTurno(
            categoria="General",
            practica="Consulta Clínica General",
            duracion_minutos=30,
            dias_habilitados="Lunes a Sábado",
            activo=True
        )
        tt_vacuna = TipoTurno(
            categoria="General",
            practica="Vacunación y Desparasitación",
            duracion_minutos=20,
            dias_habilitados="Lunes a Sábado",
            activo=True
        )
        # Prácticas particulares (días específicos y mayor duración)
        tt_castracion = TipoTurno(
            categoria="Particular",
            practica="Castración y Esterilización",
            duracion_minutos=90,
            dias_habilitados="Solo Martes y Jueves",
            activo=True
        )
        tt_ecografia = TipoTurno(
            categoria="Particular",
            practica="Ecografía Abdominal",
            duracion_minutos=45,
            dias_habilitados="Solo Miércoles y Viernes",
            activo=True
        )
        tt_analisis = TipoTurno(
            categoria="Particular",
            practica="Extracción de Sangre / Análisis",
            duracion_minutos=30,
            dias_habilitados="Lunes a Viernes",
            activo=True
        )
        # Turnos de control
        tt_control = TipoTurno(
            categoria="Control",
            practica="Control Post-Operatorio",
            duracion_minutos=20,
            dias_habilitados="Lunes a Sábado",
            activo=True
        )

        db.session.add_all([tt_consulta, tt_vacuna, tt_castracion, tt_ecografia, tt_analisis, tt_control])
        db.session.commit()

        print("5. Creando Turnos de prueba reflejando los 4 Estados del Ciclo de Vida...")
        ahora = datetime.now()

        # 1. PENDIENTE (Futuro): Bloquea la agenda para Milo
        turno_pendiente = Turno(
            usuario_id=cliente.id,
            mascota_id=perro.id,
            veterinario_id=vet1.id,
            tipo_turno_id=tt_consulta.id,
            fecha_hora=ahora + timedelta(days=2, hours=3),
            estado=Turno.ESTADO_PENDIENTE,
            observaciones="Control de rutina y vacunación anual."
        )

        # 2. ATENDIDO (Pasado): Ya cumplido en el historial de Milo
        turno_atendido = Turno(
            usuario_id=cliente.id,
            mascota_id=perro.id,
            veterinario_id=vet2.id,
            tipo_turno_id=tt_castracion.id,
            fecha_hora=ahora - timedelta(days=15),
            estado=Turno.ESTADO_ATENDIDO,
            observaciones="Castración realizada con éxito. Sin complicaciones."
        )

        # 3. AUSENTE (Pasado): El cliente no se presentó a la cita con Luna
        turno_ausente = Turno(
            usuario_id=cliente.id,
            mascota_id=gato.id,
            veterinario_id=vet3.id,
            tipo_turno_id=tt_ecografia.id,
            fecha_hora=ahora - timedelta(days=5),
            estado=Turno.ESTADO_AUSENTE,
            observaciones="Paciente no acudió a la cita médica."
        )

        # 4. CANCELADO: Anulado previamente, liberó el cupo
        turno_cancelado = Turno(
            usuario_id=cliente.id,
            mascota_id=gato.id,
            veterinario_id=vet1.id,
            tipo_turno_id=tt_vacuna.id,
            fecha_hora=ahora - timedelta(days=2),
            estado=Turno.ESTADO_CANCELADO,
            observaciones="Cancelado por el dueño 24hs antes por motivos laborales."
        )

        db.session.add_all([turno_pendiente, turno_atendido, turno_ausente, turno_cancelado])

        print("6. Creando Notificación de ejemplo...")
        noti = Notificacion(
            usuario_id=cliente.id,
            mensaje=f"Tu turno para {perro.nombre} ha sido agendado para el {(ahora + timedelta(days=2, hours=3)).strftime('%d/%m/%Y a las %H:%M')}.",
            leida=False
        )
        db.session.add(noti)

        db.session.commit()
        print("\n¡Base de datos poblada exitosamente con datos semilla!")

if __name__ == '__main__':
    poblar_base_de_datos()
