"""
Módulo con la clase GestorSistema.

Coordina las listas internas de clientes, servicios y reservas (sin base de
datos). Cada operación captura los errores, los registra en el log y
devuelve un resultado, de modo que la aplicación nunca se detiene.
"""

from .cliente import Cliente  # Clase Cliente.
from .reserva import Reserva  # Clase Reserva.
from .excepciones import SoftwareFJError, ClienteInvalidoError  # Errores propios.
from .registro import obtener_logger  # Logger del sistema.

log = obtener_logger("sistema")  # Logger propio de este módulo.


class GestorSistema:
    """Administra clientes, servicios y reservas en memoria."""

    def __init__(self):
        self._clientes = []  # Lista interna de clientes registrados.
        self._servicios = []  # Lista interna de servicios disponibles.
        self._reservas = []  # Lista interna de reservas creadas.
        log.info("===== Sistema Software FJ iniciado =====")

    # ---------------- utilidades internas ----------------
    def _registrar_error(self, operacion, error):
        """Registra un error en el log, incluida su causa encadenada si existe."""
        log.error("%s falló: %s", operacion, error)  # Error principal.
        causa = error.__cause__  # Excepción original si hubo encadenamiento.
        if causa is not None:
            log.error("   Causa original: %s", causa)  # Deja trazada la causa.

    # ---------------- clientes ----------------
    def registrar_cliente(self, nombre, documento, correo, telefono):
        """Crea y guarda un cliente. Devuelve el cliente o None si falla."""
        try:
            if any(c.documento == str(documento).strip() for c in self._clientes):
                # No se permiten dos clientes con el mismo documento.
                raise ClienteInvalidoError(f"Ya existe un cliente con el documento {documento}")
            cliente = Cliente(nombre, documento, correo, telefono)  # Puede lanzar errores de validación.
        except SoftwareFJError as error:
            self._registrar_error("Registro de cliente", error)  # Error esperado del negocio.
            return None
        else:
            self._clientes.append(cliente)  # Solo se guarda si no hubo errores.
            log.info("Cliente registrado: %s", cliente.describir())
            return cliente

    # ---------------- servicios ----------------
    def agregar_servicio(self, clase_servicio, *args, **kwargs):
        """Crea un servicio de la clase indicada. Devuelve el servicio o None."""
        try:
            servicio = clase_servicio(*args, **kwargs)  # Polimorfismo: cualquier subclase de Servicio.
        except SoftwareFJError as error:
            self._registrar_error(f"Creación de servicio {clase_servicio.__name__}", error)
            return None
        except TypeError as error:
            # Parámetros mal enviados al constructor (error de programación o de datos).
            log.error("Creación de servicio %s falló por parámetros incorrectos: %s", clase_servicio.__name__, error)
            return None
        else:
            self._servicios.append(servicio)  # Se guarda en la lista interna.
            log.info("Servicio creado: %s", servicio.describir())
            return servicio

    # ---------------- reservas ----------------
    def crear_reserva(self, cliente, servicio, duracion, **opciones):
        """Crea y confirma una reserva. Devuelve la reserva o None."""
        reserva = None  # Se inicializa para usarla en finally.
        try:
            reserva = Reserva(cliente, servicio, duracion, **opciones)  # Puede fallar si faltan datos.
            reserva.confirmar()  # Puede fallar por validaciones o disponibilidad.
        except SoftwareFJError as error:
            self._registrar_error("Creación de reserva", error)
            return None
        else:
            self._reservas.append(reserva)  # Solo se guardan las reservas confirmadas.
            return reserva
        finally:
            # Se ejecuta siempre: deja constancia del intento.
            log.debug("Intento de reserva finalizado (%s)", reserva.id if reserva else "sin crear")

    def procesar_reserva(self, reserva, impuesto=None, descuento=0.0):
        """Cobra una reserva. Devuelve el total o None si falla."""
        try:
            if reserva is None:  # No se puede procesar una reserva inexistente.
                raise SoftwareFJError("Se intentó procesar una reserva inexistente", "SFJ-401")
            return reserva.procesar(impuesto, descuento)
        except SoftwareFJError as error:
            self._registrar_error("Procesamiento de reserva", error)
            return None

    def cancelar_reserva(self, reserva, motivo="Solicitud del cliente"):
        """Cancela una reserva. Devuelve True si se canceló."""
        try:
            reserva.cancelar(motivo)
            return True
        except SoftwareFJError as error:
            self._registrar_error("Cancelación de reserva", error)
            return False

    # ---------------- consultas ----------------
    @property
    def clientes(self):
        return list(self._clientes)  # Copia: protege la lista interna.

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)
