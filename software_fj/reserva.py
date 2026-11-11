"""
Módulo con la clase Reserva.

Una reserva integra un cliente, un servicio, una duración y un estado.
Sus operaciones (confirmar, cancelar y procesar) usan las distintas formas
de manejo de excepciones que pide el proyecto:
    - try/except/else/finally en confirmar() y procesar().
    - try/finally en cancelar().
    - encadenamiento de excepciones (raise ... from ...).
"""

from enum import Enum  # Para definir los estados posibles de la reserva.
from .entidad import EntidadBase  # Clase abstracta general.
from .cliente import Cliente  # Para verificar el tipo del cliente.
from .servicios import Servicio  # Para verificar el tipo del servicio.
from .excepciones import (  # Excepciones personalizadas que usa el módulo.
    SoftwareFJError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
)
from .registro import obtener_logger  # Logger del sistema.

log = obtener_logger("reserva")  # Logger propio de este módulo.


class EstadoReserva(Enum):
    """Estados por los que pasa una reserva."""
    PENDIENTE = "pendiente"  # Creada, aún sin confirmar.
    CONFIRMADA = "confirmada"  # Validada y apartada.
    CANCELADA = "cancelada"  # Anulada por el cliente o el sistema.
    PROCESADA = "procesada"  # Cobrada; ya no se puede modificar.


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente, servicio, duracion, **opciones):
        super().__init__("RES")  # Asigna un ID con el prefijo RES.
        if cliente is None:  # El cliente es obligatorio.
            raise ParametroFaltanteError("cliente")
        if servicio is None:  # El servicio es obligatorio.
            raise ParametroFaltanteError("servicio")
        if not isinstance(cliente, Cliente):  # Debe ser un objeto Cliente.
            raise ReservaInvalidaError("El cliente indicado no es un objeto Cliente válido")
        if not isinstance(servicio, Servicio):  # Debe ser un objeto Servicio.
            raise ReservaInvalidaError("El servicio indicado no es un objeto Servicio válido")
        self._cliente = cliente  # Cliente que reserva.
        self._servicio = servicio  # Servicio reservado.
        self._duracion = duracion  # Duración en la unidad del servicio.
        self._opciones = opciones  # Opciones adicionales (asistentes, cantidad, etc.).
        self._estado = EstadoReserva.PENDIENTE  # Toda reserva inicia pendiente.
        self._costo_total = None  # Se calcula al procesar la reserva.

    @property
    def estado(self):
        """Estado actual de la reserva."""
        return self._estado

    @property
    def costo_total(self):
        """Costo total cobrado (None si aún no se ha procesado)."""
        return self._costo_total

    @property
    def cliente(self):
        """Cliente asociado a la reserva."""
        return self._cliente

    @property
    def servicio(self):
        """Servicio asociado a la reserva."""
        return self._servicio

    def validar(self):
        """Valida cliente, disponibilidad del servicio y parámetros de la reserva."""
        self._cliente.validar()  # Revalida los datos del cliente.
        if not self._servicio.disponible:  # El servicio debe estar disponible.
            raise ServicioNoDisponibleError(self._servicio.nombre)
        self._servicio.validar_parametros(self._duracion, **self._opciones)  # Reglas del servicio.
        return True

    def confirmar(self):
        """Confirma la reserva usando try/except/else/finally y encadenamiento."""
        if self._estado != EstadoReserva.PENDIENTE:  # Solo se confirma una reserva pendiente.
            raise OperacionNoPermitidaError("confirmar", self._estado.value)
        try:
            self.validar()  # Puede lanzar cualquier error de validación.
        except ServicioNoDisponibleError:
            raise  # Se relanza tal cual: el mensaje ya es claro para el usuario.
        except SoftwareFJError as error:
            # Encadenamiento: el error de validación queda como causa (__cause__).
            raise ReservaInvalidaError(f"No se pudo confirmar la reserva {self.id}") from error
        else:
            # Solo se ejecuta si validar() no lanzó ninguna excepción.
            self._estado = EstadoReserva.CONFIRMADA
            log.info("Reserva %s CONFIRMADA (%s -> %s)", self.id, self._cliente.nombre, self._servicio.nombre)
        finally:
            # Se ejecuta siempre, haya error o no: deja rastro del intento.
            log.debug("Intento de confirmación de %s finalizado; estado: %s", self.id, self._estado.value)

    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva usando try/finally."""
        try:
            if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
                # Una reserva cancelada o ya cobrada no se puede cancelar.
                raise OperacionNoPermitidaError("cancelar", self._estado.value)
            self._estado = EstadoReserva.CANCELADA  # Cambia el estado.
            log.info("Reserva %s CANCELADA. Motivo: %s", self.id, motivo)
        finally:
            # Siempre se registra el intento, aunque haya fallado.
            log.debug("Intento de cancelación de %s finalizado", self.id)

    def procesar(self, impuesto=None, descuento=0.0):
        """Calcula el costo y cobra la reserva (try/except/else/finally)."""
        if self._estado != EstadoReserva.CONFIRMADA:  # Solo se procesa una reserva confirmada.
            raise OperacionNoPermitidaError("procesar", self._estado.value)
        try:
            # Usa la variante del cálculo según los parámetros recibidos.
            costo = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        except SoftwareFJError as error:
            # Encadenamiento: el error del cálculo queda como causa del error de reserva.
            raise ReservaInvalidaError(f"No se pudo procesar el pago de {self.id}") from error
        else:
            self._costo_total = costo  # Guarda el costo calculado.
            self._estado = EstadoReserva.PROCESADA  # La reserva queda cobrada.
            log.info("Reserva %s PROCESADA. Total: $%s", self.id, f"{costo:,.2f}")
            return costo  # Devuelve el total cobrado.
        finally:
            log.debug("Intento de procesamiento de %s finalizado", self.id)

    def describir(self):
        """Descripción de la reserva."""
        total = f"${self._costo_total:,.2f}" if self._costo_total else "sin cobrar"
        return (f"{self.id} | {self._cliente.nombre} | {self._servicio.nombre} | "
                f"{self._duracion} {self._servicio.unidad}(s) | {self._estado.value} | {total}")
