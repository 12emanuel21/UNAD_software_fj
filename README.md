<div align="center">

# 🏢 Software FJ

### Sistema de gestión de clientes, servicios y reservas

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Sin dependencias](https://img.shields.io/badge/dependencias-ninguna-brightgreen)
![Pruebas](https://img.shields.io/badge/pruebas-8%20pasando-success)
![UNAD](https://img.shields.io/badge/UNAD-Programaci%C3%B3n%20213023-orange)

</div>

---

## 📌 ¿Qué es?

Software FJ es una empresa que ofrece tres servicios: **reserva de salas**, **alquiler de equipos** y **asesorías especializadas**. Este programa gestiona sus clientes, servicios y reservas usando programación orientada a objetos, **sin base de datos** (todo vive en listas en memoria).

Lo importante del proyecto es que **no se cae**: si llega un dato mal escrito, un servicio no está disponible o una reserva es imposible, el error se guarda en un archivo de logs y el programa sigue funcionando.

> Proyecto de la **Fase 4 – Prácticas simuladas** del curso **Programación (213023)** de la UNAD.
> Autor: **Emanuel Ricardo Vargas Villarreal** · Grupo 213023A_2204

---

## 🚀 Cómo ejecutarlo

Solo necesitas **Python 3.10 o superior**. No hay que instalar nada.

```bash
# Ejecutar las 18 simulaciones
python main.py

# Ejecutar las pruebas unitarias
python -m unittest discover -s tests -v
```

Al terminar, revisa el archivo **`logs/software_fj.log`**: ahí queda registrado cada evento y cada error.

---

## 🖥️ Así se ve la ejecución

```text
--- Simulación 09: Reserva de sala exitosa (costo + IVA)
    Resultado: Reserva procesada. Total con IVA: $285,600.00

--- Simulación 11: Reserva que supera la capacidad de la sala
   [LOG ERROR] Creación de reserva falló: [SFJ-400] No se pudo confirmar la reserva RES-0003
   [LOG ERROR]    Causa original: [SFJ-100] Dato inválido en 'asistentes' (25): supera la capacidad de 12 personas
    Resultado: Rechazada correctamente (supera capacidad; causa encadenada en el log)

--- Simulación 18: Error inesperado (llamada con argumentos faltantes)
   [LOG ERROR] Error inesperado en la simulación 18
    Resultado: ERROR INESPERADO controlado (ver log). El sistema continúa.

Simulaciones ejecutadas: 18. El sistema terminó sin detenerse.
```

---

## 📂 Estructura

```text
software-fj/
├── main.py              → Programa principal con las 18 simulaciones
├── software_fj/
│   ├── excepciones.py   → Mis propias excepciones (8 clases)
│   ├── registro.py      → Configuración del archivo de logs
│   ├── entidad.py       → Clase abstracta base de todo el sistema
│   ├── cliente.py       → Cliente con datos protegidos y validados
│   ├── servicios.py     → Servicio (abstracta) + Sala, Equipo y Asesoría
│   ├── reserva.py       → Reserva: confirmar, cancelar y cobrar
│   └── sistema.py       → Gestor que coordina todo sin detenerse
├── tests/
│   └── test_sistema.py  → Pruebas unitarias
└── logs/
    └── ejemplo_ejecucion.log → Copia de una ejecución completa
```

---

## ✅ Qué pedía la actividad y dónde está

| Requisito | Dónde lo encuentras |
|---|---|
| Clase abstracta general | `EntidadBase` → `entidad.py` |
| Cliente con validaciones y datos encapsulados | `Cliente` → `cliente.py` |
| Clase abstracta `Servicio` + 3 servicios | `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` → `servicios.py` |
| Polimorfismo y métodos sobrescritos | `costo_base()`, `validar_parametros()`, `describir()` |
| Métodos sobrecargados | `calcular_costo()` en 3 variantes: sin parámetros extra, con impuesto, con impuesto y descuento |
| Reserva con confirmar, cancelar y procesar | `Reserva` → `reserva.py` |
| Excepciones personalizadas | `excepciones.py` |
| `try/except/else/finally` | `Reserva.confirmar()`, `Reserva.procesar()` |
| `try/finally` | `Reserva.cancelar()` |
| Encadenamiento (`raise ... from ...`) | `Reserva.confirmar()` y `Reserva.procesar()` |
| Archivo de logs | `logs/software_fj.log` |
| Mínimo 10 simulaciones | 18 en `main.py` |

---

## 🧪 Las 18 simulaciones

| # | Qué se prueba | Resultado esperado |
|---|---|---|
| 1–2 | Registrar clientes válidos | ✅ Registrados |
| 3–5 | Correo mal escrito, documento con letras, cliente duplicado | ❌ Rechazados y registrados en el log |
| 6 | Crear sala, equipos y asesoría | ✅ Creados |
| 7–8 | Tarifa negativa, nivel de asesor inexistente | ❌ Rechazados |
| 9–10 | Reservar y cobrar (con IVA y con descuento) | ✅ Cobradas |
| 11 | Más asistentes que la capacidad de la sala | ❌ Rechazada, con la causa encadenada |
| 12 | Reservar un equipo en mantenimiento | ❌ Servicio no disponible |
| 13 | Descuento no permitido y reintento | ❌ luego ✅ |
| 14–15 | Cancelar una reserva ya cobrada / una confirmada | ❌ / ✅ |
| 16 | Cobrar con un dato dañado en memoria | ❌ Cálculo inconsistente detectado |
| 17 | Reserva sin cliente o con duración en texto | ❌ Rechazadas |
| 18 | Error de programación inesperado | ⚠️ Controlado, el programa sigue |
