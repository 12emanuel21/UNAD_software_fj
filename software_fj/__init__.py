"""
Paquete principal del Sistema Integral de Gestión de Clientes, Servicios y
Reservas de la empresa Software FJ.

El paquete reúne los módulos del sistema:
    - excepciones: jerarquía de excepciones personalizadas.
    - registro: configuración del archivo de logs.
    - entidad: clase abstracta base de todas las entidades.
    - cliente: clase Cliente con validaciones y encapsulación.
    - servicios: clase abstracta Servicio y sus tres especializaciones.
    - reserva: clase Reserva que integra cliente, servicio y duración.
    - sistema: clase GestorSistema que coordina las operaciones.
"""

# Versión del paquete; útil para identificar entregas en el repositorio.
__version__ = "1.0.0"
