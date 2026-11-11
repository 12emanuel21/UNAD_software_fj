"""
Módulo con la clase Cliente.

Los datos personales se guardan en atributos privados (con doble guion bajo)
y solo se modifican a través de propiedades que validan cada valor. Si un
dato no es válido se lanza DatoInvalidoError o ParametroFaltanteError.
"""

import re  # Expresiones regulares para validar correo y teléfono.
from .entidad import EntidadBase  # Clase abstracta base.
from .excepciones import DatoInvalidoError, ParametroFaltanteError  # Errores propios.

# Patrón sencillo de correo: texto@texto.dominio
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
# Patrón de teléfono colombiano: 10 dígitos que empiezan por 3 (celular) o 60 (fijo).
PATRON_TELEFONO = re.compile(r"^(3\d{9}|60\d{8})$")


class Cliente(EntidadBase):
    """Cliente de Software FJ con datos personales encapsulados."""

    def __init__(self, nombre, documento, correo, telefono):
        super().__init__("CLI")  # Asigna ID con el prefijo CLI.
        # Cada asignación pasa por el setter correspondiente, que valida el dato.
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    # ---------------- nombre ----------------
    @property
    def nombre(self):
        """Nombre completo del cliente."""
        return self.__nombre  # Atributo privado: no se accede desde fuera.

    @nombre.setter
    def nombre(self, valor):
        if valor is None or str(valor).strip() == "":  # El nombre es obligatorio.
            raise ParametroFaltanteError("nombre")
        valor = str(valor).strip()  # Quita espacios sobrantes.
        if len(valor) < 3:  # Un nombre real tiene al menos 3 caracteres.
            raise DatoInvalidoError("nombre", valor, "debe tener al menos 3 caracteres")
        if any(c.isdigit() for c in valor):  # Un nombre no lleva números.
            raise DatoInvalidoError("nombre", valor, "no puede contener números")
        self.__nombre = valor.title()  # Guarda el nombre con mayúscula inicial.

    # ---------------- documento ----------------
    @property
    def documento(self):
        """Número de documento de identidad."""
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if valor is None or str(valor).strip() == "":  # El documento es obligatorio.
            raise ParametroFaltanteError("documento")
        valor = str(valor).strip()  # Se trabaja siempre como texto.
        if not valor.isdigit():  # Solo se aceptan dígitos.
            raise DatoInvalidoError("documento", valor, "solo debe contener dígitos")
        if not 6 <= len(valor) <= 10:  # Longitud típica de la cédula colombiana.
            raise DatoInvalidoError("documento", valor, "debe tener entre 6 y 10 dígitos")
        self.__documento = valor  # Valor válido: se guarda.

    # ---------------- correo ----------------
    @property
    def correo(self):
        """Correo electrónico de contacto."""
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if not valor:  # El correo es obligatorio.
            raise ParametroFaltanteError("correo")
        valor = str(valor).strip().lower()  # Se normaliza a minúsculas.
        if not PATRON_CORREO.match(valor):  # Debe cumplir el patrón de correo.
            raise DatoInvalidoError("correo", valor, "formato de correo no válido")
        self.__correo = valor

    # ---------------- teléfono ----------------
    @property
    def telefono(self):
        """Teléfono de contacto (10 dígitos)."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor:  # El teléfono es obligatorio.
            raise ParametroFaltanteError("telefono")
        valor = re.sub(r"[\s-]", "", str(valor))  # Quita espacios y guiones.
        if not PATRON_TELEFONO.match(valor):  # Debe ser celular o fijo válido.
            raise DatoInvalidoError("telefono", valor, "debe tener 10 dígitos (celular 3XX o fijo 60X)")
        self.__telefono = valor

    def validar(self):
        """Revalida todos los datos; útil antes de usar el cliente en una reserva."""
        # Reasignar cada propiedad vuelve a ejecutar sus validaciones.
        self.nombre, self.documento = self.nombre, self.documento
        self.correo, self.telefono = self.correo, self.telefono
        return True  # Si no se lanzó ninguna excepción, el cliente es válido.

    def describir(self):
        """Descripción del cliente; el documento se muestra parcialmente oculto."""
        oculto = "*" * (len(self.documento) - 4) + self.documento[-4:]  # Protege el dato personal.
        return f"{self.id} | {self.nombre} | Doc. {oculto} | {self.correo}"
