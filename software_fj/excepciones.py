"""
Módulo de excepciones personalizadas del sistema Software FJ.

Se define una jerarquía propia para que cada tipo de error del negocio
tenga su propia clase. Así el programa puede capturar un error concreto
(por ejemplo, un servicio no disponible) o todos los errores del sistema
a la vez mediante la clase base SoftwareFJError.
"""


class SoftwareFJError(Exception):
    """Clase base de todas las excepciones del sistema Software FJ."""

    def __init__(self, mensaje, codigo="SFJ-000"):
        # Llama al constructor de Exception para conservar el mensaje estándar.
        super().__init__(mensaje)
        # Guarda el mensaje legible para mostrarlo al usuario o al log.
        self.mensaje = mensaje
        # Guarda un código corto que facilita buscar el error en el log.
        self.codigo = codigo

    def __str__(self):
        # Representa el error como "[código] mensaje" para el log y la consola.
        return f"[{self.codigo}] {self.mensaje}"


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando un dato no cumple el formato o el rango esperado."""

    def __init__(self, campo, valor, motivo):
        # Guarda el nombre del campo que falló la validación.
        self.campo = campo
        # Guarda el valor recibido para poder registrarlo en el log.
        self.valor = valor
        # Construye un mensaje que explica qué campo falló y por qué.
        super().__init__(f"Dato inválido en '{campo}' ({valor!r}): {motivo}", "SFJ-100")


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio."""

    def __init__(self, parametro):
        # Guarda el nombre del parámetro que no se recibió.
        self.parametro = parametro
        # Construye el mensaje con el nombre del parámetro faltante.
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", "SFJ-101")


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando no es posible registrar o usar un cliente."""

    def __init__(self, mensaje):
        # Usa el código 200 para todos los errores relacionados con clientes.
        super().__init__(mensaje, "SFJ-200")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio que no está disponible."""

    def __init__(self, nombre_servicio):
        # Guarda el nombre del servicio para el mensaje y el log.
        self.nombre_servicio = nombre_servicio
        # Construye el mensaje indicando qué servicio no se puede usar.
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "SFJ-300")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no se puede crear, confirmar o procesar."""

    def __init__(self, mensaje):
        # Usa el código 400 para todos los errores relacionados con reservas.
        super().__init__(mensaje, "SFJ-400")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando una operación no es válida en el estado actual."""

    def __init__(self, operacion, estado):
        # Guarda la operación que se intentó ejecutar.
        self.operacion = operacion
        # Guarda el estado en el que estaba el objeto al intentarla.
        self.estado = estado
        # Explica por qué la operación no es válida en ese estado.
        super().__init__(f"No se puede '{operacion}' una reserva en estado '{estado}'", "SFJ-500")


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos da un resultado imposible."""

    def __init__(self, mensaje):
        # Usa el código 600 para errores de cálculo.
        super().__init__(mensaje, "SFJ-600")
