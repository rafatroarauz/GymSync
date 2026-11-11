from datetime import datetime, timedelta

import pytest

from conftest import HOY
from gymsync.config import AMARILLA, ROJA, VERDE

AHORA = datetime(2026, 11, 11, 18, 30)


def test_sin_pago_es_roja(app, socio):
    r = app.acceso.validar(socio.id, ahora=AHORA)
    assert r.bandera == ROJA


def test_vigente_es_verde_y_registra_entrada(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)  # 30 días
    r = app.acceso.validar(socio.cedula, ahora=AHORA)
    assert r.bandera == VERDE
    entradas = app.acceso.entradas_del_dia(HOY)
    assert len(entradas) == 1 and entradas[0].socio_id == socio.id


def test_por_vencer_es_amarilla(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    cerca = datetime.combine(socio.fecha_vencimiento - timedelta(days=2), AHORA.time())
    assert app.acceso.validar(socio.id, ahora=cerca).bandera == AMARILLA
    # el último día válido sigue siendo amarillo
    ultimo = datetime.combine(socio.fecha_vencimiento, AHORA.time())
    assert app.acceso.validar(socio.id, ahora=ultimo).bandera == AMARILLA


def test_vencida_es_roja(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    despues = datetime.combine(socio.fecha_vencimiento + timedelta(days=1), AHORA.time())
    r = app.acceso.validar(socio.id, ahora=despues)
    assert r.bandera == ROJA and "vencida" in r.mensaje


def test_disciplina_no_cubierta_es_roja(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)  # Mensual Combate no cubre Musculación
    r = app.acceso.validar(socio.id, disciplina="Musculación", ahora=AHORA)
    assert r.bandera == ROJA and "no cubre" in r.mensaje


def test_socio_de_baja_es_rojo(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    app.socios.dar_de_baja(socio.id)
    assert app.acceso.validar(socio.id, ahora=AHORA).bandera == ROJA


def test_socio_inexistente_o_vacio(app):
    with pytest.raises(ValueError, match="No se encontró"):
        app.acceso.validar("A-9999")
    with pytest.raises(ValueError):
        app.acceso.validar("   ")
