"""
Módulo con la clase abstracta EntidadBase.

Representa cualquier entidad general del sistema (clientes, servicios,
reservas). Define lo que todas comparten: un identificador único, la fecha
de creación y la obligación de saber validarse y describirse.
"""

from abc import ABC, abstractmethod  # Herramientas para clases abstractas.
from datetime import datetime  # Para registrar la fecha de creación.
from collections import defaultdict  # Para llevar un contador por tipo de entidad.
import itertools  # Para generar identificadores consecutivos.


class EntidadBase(ABC):
    """Clase abstracta de la que heredan todas las entidades del sistema."""

    # Un contador independiente por prefijo (CLI, SRV, RES) para generar IDs únicos.
    _contadores = defaultdict(lambda: itertools.count(1))

    def __init__(self, prefijo):
        self._prefijo = prefijo  # Prefijo del tipo de entidad (CLI, SRV o RES).
        self._id = None  # El ID se asigna la primera vez que se consulta.
        # Guarda el momento en que se creó la entidad.
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        """Identificador único de la entidad (solo lectura), p. ej. CLI-0001."""
        if self._id is None:  # Se genera al primer uso; así los objetos rechazados no gastan números.
            self._id = f"{self._prefijo}-{next(EntidadBase._contadores[self._prefijo]):04d}"
        return self._id  # No hay setter: el ID no se puede cambiar.

    @property
    def fecha_creacion(self):
        """Fecha y hora de creación (solo lectura)."""
        return self._fecha_creacion  # Se expone sin permitir modificarla.

    @abstractmethod
    def validar(self):
        """Cada entidad define sus propias reglas de validación."""

    @abstractmethod
    def describir(self):
        """Cada entidad devuelve una descripción en texto de sí misma."""

    def __str__(self):
        # La representación en texto reutiliza el método polimórfico describir().
        return self.describir()
