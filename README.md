# GymSync — Etapa 2: Programación modular

Sistema administrativo de escritorio para gimnasios. Universidad Americana, Programación Estructurada.
Autores: Rafael Antonio Arauz Navarro y Maria Regina Medrano Flores.

Esta entrega incluye los **módulos, procedimientos, funciones y manejo de archivos binarios**.
La interfaz es de consola de forma temporal; la GUI en Tkinter corresponde a la Etapa 5.

## Cómo ejecutar
Requiere Python 3.10 o superior. Desde la carpeta `ProyectoFinal/`:

```bash
python -m gymsync.main        # programa (menú 5 → 5 carga 10 socios de ejemplo)
python -m pip install -r requirements.txt
python -m pytest -v           # 34 pruebas unitarias
```

Las carpetas `data/`, `comprobantes/`, `reportes/` y `backups/` se crean solas.
Para empezar desde cero, basta con borrarlas.

## Arquitectura (según el diagrama modular de la Fase 1)
```
ui/consola.py ──► services/ ──► models/ · algorithms/ · structures/
                      └───────► storage/ (archivos binarios .dat)
```
La interfaz solo llama a `services`. Los servicios validan y lanzan `ValueError` con un
mensaje claro, y la UI los atrapa en un único punto (`ejecutar_opcion`), así que el programa
no se cae por un dato mal ingresado.

| Módulo | Contenido | Requisito |
|---|---|---|
| `models/` | `Socio`, `Plan`, `Pago`, `Entrada`, `Disciplina` (dataclasses) | — |
| `storage/archivo_binario.py` | `guardar()` y `cargar()` con pickle; escritura atómica; detecta archivos dañados | RNF1 |
| `storage/repositorio.py` | `Repositorio`: CRUD genérico sincronizado con su `.dat` | RNF1 |
| `storage/respaldo.py` | `respaldar()`: copia los `.dat` a `backups/fecha_hora/` | RF7 |
| `algorithms/ordenamiento.py` | `merge_sort()` genérico y estable, O(n log n) | — |
| `algorithms/busqueda.py` | `busqueda_binaria()` genérica, O(log n) | RNF2 |
| `services/socios_service.py` | Alta, consulta, edición, baja lógica, estado y listado. Índices ordenados por ID y cédula | RF1 |
| `services/acceso_service.py` | Molinete virtual: bandera VERDE / AMARILLA / ROJA y registro de entradas | RF2 |
| `services/pagos_service.py` | Cobro y renovación, comprobante `.txt`, próximos vencimientos, morosos | RF3 |
| `services/reportes_service.py` | CSV de ingresos, asistencia y morosos | RF6 |
| `services/config_service.py` | Planes y disciplinas (con datos iniciales) | RF7 |
| `structures/` | Reservado para AVL, heaps y grafos (Etapa 3) | RF1–RF5 |
| `ui/consola.py` | Menús; cada opción es un procedimiento | RNF3 |
| `app.py` | `crear_app()`: ensambla repositorios y servicios | — |

## Reglas del molinete (RF2)
- **ROJA:** socio dado de baja, sin membresía pagada, membresía vencida o plan que no cubre la disciplina.
- **AMARILLA:** acceso permitido, pero vence en 3 días o menos (`UMBRAL_POR_VENCER_DIAS` en `config.py`).
- **VERDE:** acceso permitido.

Toda validación queda registrada en `entradas.dat` con fecha y hora.

## Procedimientos vs. funciones (ejemplos)
- **Funciones** (devuelven un valor): `merge_sort`, `busqueda_binaria`, `cargar`,
  `AccesoService.evaluar`, `PagosService.calcular_vencimiento`, `SociosService.estado`, `a_fecha`.
- **Procedimientos** (realizan una acción): `guardar`, `Repositorio.anexar`, `imprimir_tabla`,
  `registrar_socio`, `menu_molinete`, `ver_morosos`.

## Pruebas (`tests/`)
| Archivo | Qué verifica |
|---|---|
| `test_algoritmos.py` | merge sort (estabilidad, orden inverso, casos borde) y búsqueda binaria |
| `test_storage.py` | guardar/cargar, archivo corrupto, CRUD persistente, datos tras reiniciar, respaldo |
| `test_socios.py` | ID consecutivo, cédula duplicada, campos obligatorios, plan sin cobertura, fecha inválida, edición y baja |
| `test_acceso.py` | las tres banderas, vencida, disciplina no cubierta, socio inexistente |
| `test_pagos.py` | cálculo de vencimiento, renovación, validaciones, vencimientos/morosos, CSV |
