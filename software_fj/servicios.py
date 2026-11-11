"""
Módulo de servicios de Software FJ.

Contiene la clase abstracta Servicio y tres servicios especializados:
    - ReservaSala: alquiler de salas por horas.
    - AlquilerEquipo: alquiler de equipos por días.
    - AsesoriaEspecializada: asesorías por horas según el nivel del asesor.

Cada servicio sobrescribe los métodos para calcular su costo base,
validar sus parámetros y describirse (polimorfismo).
"""

from abc import abstractmethod  # Para declarar métodos abstractos.
from typing import overload  # Para documentar las variantes del cálculo de costos.
from .entidad import EntidadBase  # Clase abstracta general.
from .excepciones import (  # Excepciones personalizadas que usa el módulo.
    DatoInvalidoError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)
from .registro import obtener_logger  # Logger del sistema.

log = obtener_logger("servicios")  # Logger propio de este módulo.

IVA = 0.19  # Tarifa general de IVA en Colombia, usada como impuesto por defecto.


class Servicio(EntidadBase):
    """Clase abstracta para todos los servicios que ofrece Software FJ."""

    def __init__(self, nombre, tarifa, disponible=True):
        super().__init__("SRV")  # Asigna un ID con el prefijo SRV.
        if not nombre or not str(nombre).strip():  # El nombre es obligatorio.
            raise ParametroFaltanteError("nombre del servicio")
        self._nombre = str(nombre).strip()  # Nombre del servicio.
        if not isinstance(tarifa, (int, float)) or tarifa <= 0:  # La tarifa debe ser positiva.
            raise DatoInvalidoError("tarifa", tarifa, "debe ser un número mayor que cero")
        self._tarifa = float(tarifa)  # Tarifa por unidad de tiempo.
        self._disponible = bool(disponible)  # Indica si se puede reservar.

    @property
    def nombre(self):
        """Nombre del servicio."""
        return self._nombre

    @property
    def tarifa(self):
        """Tarifa por unidad de tiempo (hora o día según el servicio)."""
        return self._tarifa

    @property
    def disponible(self):
        """True si el servicio se puede reservar."""
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        """Habilita o deshabilita el servicio (por ejemplo, por mantenimiento)."""
        self._disponible = bool(estado)  # Actualiza la disponibilidad.
        log.info("Servicio %s ahora %s", self.nombre, "disponible" if estado else "NO disponible")

    # ------------- métodos que cada servicio debe sobrescribir -------------
    @abstractmethod
    def costo_base(self, duracion):
        """Costo sin impuestos ni descuentos para la duración indicada."""

    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Valida la duración y las opciones propias de cada servicio."""

    @property
    @abstractmethod
    def unidad(self):
        """Unidad en que se mide la duración ('hora' o 'día')."""

    # ------------- cálculo de costos "sobrecargado" -------------
    # Python no permite varias funciones con el mismo nombre; la sobrecarga se
    # simula con parámetros opcionales. Las firmas @overload documentan las
    # tres variantes que acepta calcular_costo().
    @overload
    def calcular_costo(self, duracion: float) -> float: ...
    @overload
    def calcular_costo(self, duracion: float, impuesto: float) -> float: ...
    @overload
    def calcular_costo(self, duracion: float, impuesto: float, descuento: float) -> float: ...

    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        """
        Calcula el costo total del servicio.

        Variantes:
            calcular_costo(d)            -> costo base + IVA del 19 %.
            calcular_costo(d, imp)       -> costo base + impuesto indicado.
            calcular_costo(d, imp, desc) -> aplica descuento y luego impuesto.
        """
        impuesto = IVA if impuesto is None else impuesto  # Variante 1: IVA por defecto.
        if not 0 <= impuesto <= 1:  # El impuesto se expresa entre 0 y 1.
            raise DatoInvalidoError("impuesto", impuesto, "debe estar entre 0 y 1")
        if not 0 <= descuento < 1:  # Un descuento del 100 % o más no tiene sentido.
            raise DatoInvalidoError("descuento", descuento, "debe estar entre 0 y 0,99")
        base = self.costo_base(duracion)  # Llamada polimórfica: cada servicio calcula su base.
        total = base * (1 - descuento) * (1 + impuesto)  # Aplica descuento y luego impuesto.
        if total <= 0 or total != total:  # Total no positivo o NaN: cálculo inconsistente.
            raise CalculoInconsistenteError(f"Costo calculado inválido ({total}) para {self.nombre}")
        return round(total, 2)  # Redondea a dos decimales (pesos y centavos).

    def _validar_duracion(self, duracion, minimo, maximo):
        """Validación común de la duración, reutilizada por las subclases."""
        if duracion is None:  # La duración es obligatoria.
            raise ParametroFaltanteError("duracion")
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool):  # Debe ser numérica.
            raise DatoInvalidoError("duracion", duracion, "debe ser un número")
        if not minimo <= duracion <= maximo:  # Debe estar dentro del rango permitido.
            raise DatoInvalidoError("duracion", duracion, f"debe estar entre {minimo} y {maximo} {self.unidad}(s)")

    def validar(self):
        """Valida que el servicio tenga nombre y tarifa coherentes."""
        if self._tarifa <= 0:  # Protección adicional ante cambios internos.
            raise DatoInvalidoError("tarifa", self._tarifa, "debe ser mayor que cero")
        return True


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o capacitación, cobrada por hora."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)  # Inicializa la parte común.
        if not isinstance(capacidad, int) or capacidad <= 0:  # La capacidad es un entero positivo.
            raise DatoInvalidoError("capacidad", capacidad, "debe ser un entero mayor que cero")
        self._capacidad = capacidad  # Número máximo de personas.

    @property
    def unidad(self):
        return "hora"  # Las salas se cobran por hora.

    def costo_base(self, duracion):
        # Sobrescritura: tarifa por hora; desde 8 horas se cobra como día completo (8 h).
        horas = min(duracion, 8)  # Tope de cobro de 8 horas.
        return self.tarifa * horas

    def validar_parametros(self, duracion, **opciones):
        # Sobrescritura: entre 1 y 12 horas y asistentes dentro de la capacidad.
        self._validar_duracion(duracion, 1, 12)
        asistentes = opciones.get("asistentes")  # Número de personas esperadas.
        if asistentes is None:  # Para una sala es obligatorio saber cuántos asisten.
            raise ParametroFaltanteError("asistentes")
        if asistentes > self._capacidad:  # No se puede superar la capacidad.
            raise DatoInvalidoError("asistentes", asistentes, f"supera la capacidad de {self._capacidad} personas")

    def describir(self):
        # Sobrescritura: descripción específica de la sala.
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.id} | Sala '{self.nombre}' | {self._capacidad} personas | ${self.tarifa:,.0f}/hora | {estado}"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portátiles, proyectores, etc.), cobrado por día."""

    def __init__(self, nombre, tarifa_dia, unidades_disponibles, disponible=True):
        super().__init__(nombre, tarifa_dia, disponible)  # Inicializa la parte común.
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:  # Inventario válido.
            raise DatoInvalidoError("unidades_disponibles", unidades_disponibles, "debe ser un entero no negativo")
        self._unidades = unidades_disponibles  # Unidades del equipo en inventario.
        self._cantidad_reservada = 1  # Cantidad de la última validación (para el costo).

    @property
    def unidad(self):
        return "día"  # Los equipos se cobran por día.

    def costo_base(self, duracion):
        # Sobrescritura: tarifa diaria por número de unidades alquiladas.
        return self.tarifa * duracion * self._cantidad_reservada

    def validar_parametros(self, duracion, **opciones):
        # Sobrescritura: entre 1 y 30 días y cantidad dentro del inventario.
        self._validar_duracion(duracion, 1, 30)
        cantidad = opciones.get("cantidad", 1)  # Por defecto se alquila una unidad.
        if not isinstance(cantidad, int) or cantidad <= 0:  # Debe ser un entero positivo.
            raise DatoInvalidoError("cantidad", cantidad, "debe ser un entero mayor que cero")
        if cantidad > self._unidades:  # No se puede alquilar más de lo que hay.
            raise DatoInvalidoError("cantidad", cantidad, f"solo hay {self._unidades} unidad(es) disponibles")
        self._cantidad_reservada = cantidad  # Se guarda para calcular el costo.

    def describir(self):
        # Sobrescritura: descripción específica del equipo.
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.id} | Equipo '{self.nombre}' | {self._unidades} unidades | ${self.tarifa:,.0f}/día | {estado}"


class AsesoriaEspecializada(Servicio):
    """Asesoría profesional cobrada por hora según el nivel del asesor."""

    # Recargo según el nivel del asesor (polimorfismo de datos).
    RECARGOS = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, area, nivel="junior", disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)  # Inicializa la parte común.
        if not area:  # El área de la asesoría es obligatoria.
            raise ParametroFaltanteError("area")
        nivel = str(nivel).lower()  # Normaliza el nivel a minúsculas.
        if nivel not in self.RECARGOS:  # Solo se aceptan los niveles definidos.
            raise DatoInvalidoError("nivel", nivel, f"debe ser uno de {list(self.RECARGOS)}")
        self._area = area  # Área de conocimiento (p. ej., ciberseguridad).
        self._nivel = nivel  # Nivel del asesor.

    @property
    def unidad(self):
        return "hora"  # Las asesorías se cobran por hora.

    def costo_base(self, duracion):
        # Sobrescritura: tarifa por hora multiplicada por el recargo del nivel.
        return self.tarifa * duracion * self.RECARGOS[self._nivel]

    def calcular_costo(self, duracion, impuesto=None, descuento=0.0):
        # Sobrescritura que extiende al padre: las asesorías de nivel experto
        # no admiten descuentos mayores al 10 %.
        if self._nivel == "experto" and descuento > 0.10:
            raise DatoInvalidoError("descuento", descuento, "las asesorías de nivel experto admiten máximo 10 %")
        return super().calcular_costo(duracion, impuesto, descuento)  # Reutiliza el cálculo general.

    def validar_parametros(self, duracion, **opciones):
        # Sobrescritura: entre 1 y 8 horas por sesión.
        self._validar_duracion(duracion, 1, 8)

    def describir(self):
        # Sobrescritura: descripción específica de la asesoría.
        estado = "Disponible" if self.disponible else "No disponible"
        return (f"{self.id} | Asesoría '{self.nombre}' | Área: {self._area} | "
                f"Nivel: {self._nivel} | ${self.tarifa:,.0f}/hora | {estado}")
