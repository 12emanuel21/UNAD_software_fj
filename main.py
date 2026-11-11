"""
Programa principal del Sistema Integral de Gestión de Clientes, Servicios y
Reservas de Software FJ.

Ejecuta una serie de simulaciones con operaciones válidas e inválidas para
demostrar que el sistema registra cada error en logs/software_fj.log y sigue
funcionando sin detenerse.

Ejecución:  python main.py
"""

from software_fj.sistema import GestorSistema  # Coordinador del sistema.
from software_fj.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada  # Servicios.
from software_fj.registro import obtener_logger, ARCHIVO_LOG  # Logger y ruta del archivo de logs.

log = obtener_logger("main")  # Logger del programa principal.
resultados = []  # Lista con (número, descripción, resultado) de cada simulación.


def ejecutar_simulacion(numero, descripcion, funcion):
    """
    Ejecuta una simulación protegida.

    Si ocurre un error inesperado (que no sea del negocio), se registra con su
    traza completa en el log y el programa continúa con la siguiente simulación.
    """
    print(f"\n--- Simulación {numero:02d}: {descripcion}")  # Encabezado en consola.
    log.info("Simulación %02d iniciada: %s", numero, descripcion)
    try:
        resultado = funcion()  # Ejecuta la operación simulada.
    except Exception:  # Red de seguridad para errores no previstos.
        log.exception("Error inesperado en la simulación %02d", numero)  # Guarda la traza.
        print("    Resultado: ERROR INESPERADO controlado (ver log). El sistema continúa.")
        resultados.append((numero, descripcion, "Error inesperado controlado"))
    else:
        print(f"    Resultado: {resultado}")  # Muestra el resultado de la operación.
        resultados.append((numero, descripcion, resultado))
    finally:
        log.info("Simulación %02d finalizada", numero)  # Siempre deja constancia.


def main():
    sistema = GestorSistema()  # Crea el sistema con sus listas vacías.
    datos = {}  # Diccionario para compartir objetos entre simulaciones.

    # 01 - Registro válido de un cliente.
    def sim01():
        datos["ana"] = sistema.registrar_cliente("ana maría torres", "1045789632", "ana.torres@gmail.com", "3014567890")
        return f"Cliente registrado: {datos['ana']}" if datos["ana"] else "Falló"
    ejecutar_simulacion(1, "Registrar cliente válido (Ana)", sim01)

    # 02 - Segundo registro válido.
    def sim02():
        datos["carlos"] = sistema.registrar_cliente("Carlos Pérez", "72345678", "cperez@empresa.co", "605 3456789")
        return f"Cliente registrado: {datos['carlos']}" if datos["carlos"] else "Falló"
    ejecutar_simulacion(2, "Registrar cliente válido (Carlos, teléfono fijo)", sim02)

    # 03 - Cliente con correo inválido.
    def sim03():
        cliente = sistema.registrar_cliente("Luisa Gómez", "1098765432", "luisa.gomez@", "3157778899")
        return "Rechazado correctamente (correo inválido)" if cliente is None else "ERROR: se aceptó"
    ejecutar_simulacion(3, "Registrar cliente con correo inválido", sim03)

    # 04 - Cliente con documento que contiene letras.
    def sim04():
        cliente = sistema.registrar_cliente("Pedro Ruiz", "10A45B", "pedro@gmail.com", "3001234567")
        return "Rechazado correctamente (documento inválido)" if cliente is None else "ERROR: se aceptó"
    ejecutar_simulacion(4, "Registrar cliente con documento inválido", sim04)

    # 05 - Cliente duplicado (mismo documento que Ana).
    def sim05():
        cliente = sistema.registrar_cliente("Ana Duplicada", "1045789632", "otra@gmail.com", "3014567891")
        return "Rechazado correctamente (documento duplicado)" if cliente is None else "ERROR: se aceptó"
    ejecutar_simulacion(5, "Registrar cliente duplicado", sim05)

    # 06 - Creación correcta de los tres tipos de servicio.
    def sim06():
        datos["sala"] = sistema.agregar_servicio(ReservaSala, "Sala Innovación", 80000, capacidad=12)
        datos["equipo"] = sistema.agregar_servicio(AlquilerEquipo, "Portátil Core i7", 45000, unidades_disponibles=5)
        datos["proyector"] = sistema.agregar_servicio(AlquilerEquipo, "Proyector 4K", 60000, unidades_disponibles=2)
        datos["asesoria"] = sistema.agregar_servicio(AsesoriaEspecializada, "Auditoría de seguridad", 120000,
                                                     area="Ciberseguridad", nivel="experto")
        creados = [s for s in (datos["sala"], datos["equipo"], datos["proyector"], datos["asesoria"]) if s]
        return f"{len(creados)} servicios creados correctamente"
    ejecutar_simulacion(6, "Crear servicios válidos (sala, equipos y asesoría)", sim06)

    # 07 - Servicio con tarifa negativa.
    def sim07():
        servicio = sistema.agregar_servicio(ReservaSala, "Sala Fantasma", -5000, capacidad=10)
        return "Rechazado correctamente (tarifa negativa)" if servicio is None else "ERROR: se aceptó"
    ejecutar_simulacion(7, "Crear servicio con tarifa negativa", sim07)

    # 08 - Asesoría con un nivel que no existe.
    def sim08():
        servicio = sistema.agregar_servicio(AsesoriaEspecializada, "Asesoría Cloud", 90000, area="Nube", nivel="maestro")
        return "Rechazado correctamente (nivel inexistente)" if servicio is None else "ERROR: se aceptó"
    ejecutar_simulacion(8, "Crear asesoría con nivel inexistente", sim08)

    # 09 - Reserva exitosa de sala y cobro con IVA por defecto (variante 1 del cálculo).
    def sim09():
        datos["res_sala"] = sistema.crear_reserva(datos["ana"], datos["sala"], 3, asistentes=10)
        total = sistema.procesar_reserva(datos["res_sala"])  # calcular_costo(duracion)
        return f"Reserva procesada. Total con IVA: ${total:,.2f}" if total else "Falló"
    ejecutar_simulacion(9, "Reserva de sala exitosa (costo + IVA)", sim09)

    # 10 - Reserva exitosa de equipos con descuento (variante 3 del cálculo).
    def sim10():
        reserva = sistema.crear_reserva(datos["carlos"], datos["equipo"], 5, cantidad=3)
        total = sistema.procesar_reserva(reserva, 0.19, 0.10)  # calcular_costo(d, imp, desc)
        return f"3 portátiles x 5 días con 10 % de descuento: ${total:,.2f}" if total else "Falló"
    ejecutar_simulacion(10, "Alquiler de equipos con descuento", sim10)

    # 11 - Reserva inválida: los asistentes superan la capacidad (encadenamiento).
    def sim11():
        reserva = sistema.crear_reserva(datos["carlos"], datos["sala"], 2, asistentes=25)
        return "Rechazada correctamente (supera capacidad; causa encadenada en el log)" if reserva is None else "ERROR"
    ejecutar_simulacion(11, "Reserva que supera la capacidad de la sala", sim11)

    # 12 - Servicio no disponible (proyector en mantenimiento).
    def sim12():
        datos["proyector"].cambiar_disponibilidad(False)  # Se pone en mantenimiento.
        reserva = sistema.crear_reserva(datos["ana"], datos["proyector"], 2, cantidad=1)
        return "Rechazada correctamente (servicio no disponible)" if reserva is None else "ERROR"
    ejecutar_simulacion(12, "Reservar un servicio no disponible", sim12)

    # 13 - Asesoría experta: descuento no permitido y luego cobro sin impuesto (variante 2).
    def sim13():
        reserva = sistema.crear_reserva(datos["ana"], datos["asesoria"], 4)
        fallido = sistema.procesar_reserva(reserva, 0.19, 0.20)  # 20 % no permitido para experto.
        total = sistema.procesar_reserva(reserva, 0.0)  # calcular_costo(d, imp): exento de IVA.
        estado = "rechazado" if fallido is None else "aceptado por error"
        return (f"Descuento del 20 % {estado}; reintento exento de IVA: ${total:,.2f}"
                if total else "Falló")
    ejecutar_simulacion(13, "Asesoría experta con descuento no permitido y reintento", sim13)

    # 14 - Operaciones no permitidas: cancelar una reserva ya procesada.
    def sim14():
        ok = sistema.cancelar_reserva(datos["res_sala"], "El cliente cambió de fecha")
        return "Rechazada correctamente (no se cancela una reserva procesada)" if not ok else "ERROR"
    ejecutar_simulacion(14, "Cancelar una reserva ya procesada", sim14)

    # 15 - Cancelación válida de una reserva confirmada.
    def sim15():
        reserva = sistema.crear_reserva(datos["carlos"], datos["sala"], 2, asistentes=4)
        ok = sistema.cancelar_reserva(reserva, "Reunión aplazada")
        return f"Reserva cancelada: {reserva}" if ok else "Falló"
    ejecutar_simulacion(15, "Cancelar una reserva confirmada", sim15)

    # 16 - Cálculo inconsistente por un dato corrupto en memoria.
    def sim16():
        sala_b = sistema.agregar_servicio(ReservaSala, "Sala Auditorio", 150000, capacidad=40)
        reserva = sistema.crear_reserva(datos["ana"], sala_b, 4, asistentes=30)
        sala_b._tarifa = -150000  # Simula un dato dañado después de crear la reserva.
        total = sistema.procesar_reserva(reserva)
        sala_b._tarifa = 150000  # Se restaura el dato para no afectar otras operaciones.
        return "Detectado cálculo inconsistente; la reserva no se cobró" if total is None else "ERROR"
    ejecutar_simulacion(16, "Procesar reserva con un dato corrupto (cálculo inconsistente)", sim16)

    # 17 - Reserva con parámetros faltantes y duración con tipo incorrecto.
    def sim17():
        sin_cliente = sistema.crear_reserva(None, datos["sala"], 2, asistentes=5)
        texto = sistema.crear_reserva(datos["ana"], datos["equipo"], "tres", cantidad=1)
        return ("Rechazadas correctamente (cliente faltante y duración no numérica)"
                if sin_cliente is None and texto is None else "ERROR")
    ejecutar_simulacion(17, "Reservas con parámetros faltantes o mal tipados", sim17)

    # 18 - Error inesperado de programación: faltan argumentos al registrar un cliente.
    def sim18():
        return sistema.registrar_cliente("Sin Datos")  # TypeError: faltan argumentos.
    ejecutar_simulacion(18, "Error inesperado (llamada con argumentos faltantes)", sim18)

    # ---------------- resumen final ----------------
    print("\n" + "=" * 70)
    print("RESUMEN DE LA EJECUCIÓN")
    print("=" * 70)
    print(f"Clientes registrados: {len(sistema.clientes)}")
    for c in sistema.clientes:
        print(f"   {c}")
    print(f"Servicios creados: {len(sistema.servicios)}")
    for s in sistema.servicios:
        print(f"   {s}")
    print(f"Reservas confirmadas: {len(sistema.reservas)}")
    for r in sistema.reservas:
        print(f"   {r}")
    print(f"\nSimulaciones ejecutadas: {len(resultados)}. El sistema terminó sin detenerse.")
    print(f"Detalle de eventos y errores en: {ARCHIVO_LOG}")
    log.info("===== Ejecución finalizada: %d simulaciones =====", len(resultados))


if __name__ == "__main__":  # Solo se ejecuta al correr el archivo directamente.
    main()
