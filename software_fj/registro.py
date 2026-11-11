"""
Módulo de configuración del registro de eventos (logging).

Todos los módulos obtienen su logger con obtener_logger(). Los mensajes se
guardan en logs/software_fj.log y los de nivel WARNING o superior también se
muestran en consola.
"""

import logging  # Módulo estándar de Python para registrar eventos.
import os  # Permite construir rutas y crear la carpeta de logs.

# Carpeta donde se guardará el archivo de logs (en la raíz del proyecto).
CARPETA_LOGS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
# Ruta completa del archivo de logs.
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")
# Formato de cada línea: fecha, nivel, módulo y mensaje.
FORMATO = "%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s"

# Bandera para no configurar el logging dos veces si se importa varias veces.
_configurado = False


class FormatoConsola(logging.Formatter):
    """Formato de consola que muestra el mensaje sin la traza completa del error."""

    def format(self, record):
        copia = logging.makeLogRecord(record.__dict__)  # Copia para no alterar el registro del archivo.
        copia.exc_info = None  # Quita la traza: en consola solo se muestra el mensaje.
        copia.exc_text = None  # Quita la traza ya formateada, si existe.
        return super().format(copia)


def configurar_logging(nivel=logging.INFO):
    """Configura el logger raíz del sistema una sola vez."""
    global _configurado  # Se modifica la bandera del módulo.
    if _configurado:  # Si ya se configuró, no se repite.
        return
    os.makedirs(CARPETA_LOGS, exist_ok=True)  # Crea la carpeta si no existe.
    logger = logging.getLogger("software_fj")  # Logger raíz del paquete.
    logger.setLevel(nivel)  # Nivel mínimo de mensajes que se registran.

    # Manejador que escribe en el archivo de logs en UTF-8 (tildes y ñ).
    archivo = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    archivo.setFormatter(logging.Formatter(FORMATO))  # Aplica el formato.
    logger.addHandler(archivo)  # Agrega el manejador al logger.

    # Manejador de consola solo para advertencias y errores.
    consola = logging.StreamHandler()
    consola.setLevel(logging.WARNING)  # Evita llenar la consola con INFO.
    consola.setFormatter(FormatoConsola("   [LOG %(levelname)s] %(message)s"))
    logger.addHandler(consola)  # Agrega el manejador de consola.

    _configurado = True  # Marca que la configuración ya se hizo.


def obtener_logger(nombre):
    """Devuelve un logger hijo de 'software_fj' para el módulo indicado."""
    configurar_logging()  # Garantiza que el logging esté configurado.
    return logging.getLogger(f"software_fj.{nombre}")  # Logger del módulo.
