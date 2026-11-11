"""
Pruebas unitarias del sistema Software FJ.

Ejecución:  python -m unittest discover -s tests -v
"""

import unittest  # Framework de pruebas de la biblioteca estándar.
from software_fj.cliente import Cliente
from software_fj.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from software_fj.reserva import Reserva, EstadoReserva
from software_fj.excepciones import (
    DatoInvalidoError, ParametroFaltanteError, ReservaInvalidaError,
    ServicioNoDisponibleError, OperacionNoPermitidaError,
)


class PruebasCliente(unittest.TestCase):
    def test_cliente_valido(self):
        c = Cliente("ana torres", "1045789632", "ana@gmail.com", "3014567890")
        self.assertEqual(c.nombre, "Ana Torres")  # El nombre se normaliza.

    def test_correo_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            Cliente("Ana Torres", "1045789632", "ana@", "3014567890")

    def test_nombre_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            Cliente("", "1045789632", "ana@gmail.com", "3014567890")


class PruebasServicios(unittest.TestCase):
    def setUp(self):
        self.sala = ReservaSala("Sala A", 100000, capacidad=10)

    def test_variantes_de_costo(self):
        self.assertEqual(self.sala.calcular_costo(2), 238000.0)  # Con IVA por defecto.
        self.assertEqual(self.sala.calcular_costo(2, 0.0), 200000.0)  # Sin impuesto.
        self.assertEqual(self.sala.calcular_costo(2, 0.0, 0.5), 100000.0)  # Con descuento.

    def test_polimorfismo_costo_base(self):
        equipo = AlquilerEquipo("Portátil", 50000, unidades_disponibles=4)
        asesoria = AsesoriaEspecializada("Datos", 100000, area="BI", nivel="senior")
        equipo.validar_parametros(2, cantidad=2)
        self.assertEqual(equipo.costo_base(2), 200000)  # 50.000 x 2 días x 2 unidades.
        self.assertEqual(asesoria.costo_base(2), 300000)  # 100.000 x 2 h x 1,5.


class PruebasReserva(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente("Carlos Pérez", "72345678", "c@empresa.co", "3001234567")
        self.sala = ReservaSala("Sala B", 80000, capacidad=5)

    def test_encadenamiento_de_excepciones(self):
        reserva = Reserva(self.cliente, self.sala, 2, asistentes=20)
        with self.assertRaises(ReservaInvalidaError) as ctx:
            reserva.confirmar()
        self.assertIsInstance(ctx.exception.__cause__, DatoInvalidoError)  # Causa encadenada.

    def test_servicio_no_disponible(self):
        self.sala.cambiar_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponibleError):
            Reserva(self.cliente, self.sala, 2, asistentes=3).confirmar()

    def test_no_cancelar_reserva_procesada(self):
        reserva = Reserva(self.cliente, self.sala, 2, asistentes=3)
        reserva.confirmar()
        reserva.procesar()
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar()


if __name__ == "__main__":
    unittest.main()
