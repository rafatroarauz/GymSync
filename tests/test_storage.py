from datetime import date

import pytest

from gymsync.app import crear_app
from gymsync.models import Socio
from gymsync.storage import archivo_binario
from gymsync.storage.archivo_binario import ErrorArchivo
from gymsync.storage.repositorio import Repositorio


def test_guardar_y_cargar_devuelve_lo_mismo(tmp_path):
    ruta = tmp_path / "data" / "socios.dat"
    socios = [Socio("A-1001", "001", "Ana", "8888", "MMA", "Mensual", date(2026, 11, 1))]
    archivo_binario.guardar(socios, ruta)
    assert archivo_binario.cargar(ruta) == socios


def test_cargar_archivo_inexistente_devuelve_lista_vacia(tmp_path):
    assert archivo_binario.cargar(tmp_path / "no_existe.dat") == []


def test_archivo_corrupto_lanza_error_claro(tmp_path):
    ruta = tmp_path / "socios.dat"
    ruta.write_bytes(b"esto no es pickle")
    with pytest.raises(ErrorArchivo):
        archivo_binario.cargar(ruta)


def test_repositorio_crud_persiste_en_disco(tmp_path):
    ruta = tmp_path / "socios.dat"
    repo = Repositorio(ruta, clave="id")
    socio = Socio("A-1001", "001", "Ana", "8888", "MMA", "Mensual", date(2026, 11, 1))
    repo.agregar(socio)
    with pytest.raises(ValueError):
        repo.agregar(socio)  # clave duplicada

    socio.nombre = "Ana María"
    repo.actualizar(socio)
    assert Repositorio(ruta, clave="id").obtener("A-1001").nombre == "Ana María"

    repo.eliminar("A-1001")
    assert Repositorio(ruta, clave="id").cantidad() == 0


def test_los_datos_sobreviven_al_reiniciar_la_app(tmp_path):
    app = crear_app(tmp_path)
    socio = app.socios.registrar("001-1", "Ana", "8888", "MMA", "Mensual Combate")
    app.pagos.cobrar(socio.id)
    app.acceso.validar(socio.id)

    reiniciada = crear_app(tmp_path)
    assert reiniciada.socios.buscar_por_id(socio.id).fecha_vencimiento is not None
    assert reiniciada.pagos.repo_pagos.cantidad() == 1
    assert reiniciada.acceso.repo_entradas.cantidad() == 1


def test_respaldo_copia_los_archivos(app):
    app.socios.registrar("001-1", "Ana", "8888", "MMA", "Mensual Combate")
    destino = app.respaldar()
    assert (destino / "socios.dat").exists()
    assert (destino / "planes.dat").exists()
