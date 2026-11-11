import csv
from datetime import date, timedelta

import pytest

from conftest import HOY


def test_primer_cobro_cuenta_hoy_como_dia_uno(app, socio):
    pago, ruta = app.pagos.cobrar(socio.id, hoy=HOY)
    assert pago.comprobante == "P-0001"
    assert pago.monto == 1100.0
    assert socio.fecha_vencimiento == HOY + timedelta(days=29)
    texto = ruta.read_text(encoding="utf-8")
    assert "P-0001" in texto and "María López" in texto and "1,100.00" in texto


def test_renovar_desde_vencimiento_extiende_la_fecha(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    vence = socio.fecha_vencimiento
    app.pagos.cobrar(socio.id, hoy=HOY + timedelta(days=5))
    assert socio.fecha_vencimiento == vence + timedelta(days=30)


def test_renovar_desde_hoy_ignora_el_vencimiento(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    dia = HOY + timedelta(days=5)
    app.pagos.cobrar(socio.id, desde_vencimiento=False, hoy=dia)
    assert socio.fecha_vencimiento == dia + timedelta(days=29)


def test_cambio_de_plan_y_validaciones(app, socio):
    app.pagos.cobrar(socio.id, plan="Trimestral Full", hoy=HOY)
    assert socio.plan == "Trimestral Full"
    with pytest.raises(ValueError, match="Método"):
        app.pagos.cobrar(socio.id, metodo="Bitcoin", hoy=HOY)
    with pytest.raises(ValueError, match="no cubre"):
        app.pagos.cobrar(socio.id, plan="Mensual Musculación", hoy=HOY)


def test_proximos_vencimientos_y_morosos(app, socio):
    otro = app.socios.registrar("002", "Carlos", "7550", "Musculación", "Mensual Musculación")
    app.pagos.cobrar(socio.id, hoy=HOY - timedelta(days=25))   # vence en 4 días
    app.pagos.cobrar(otro.id, hoy=HOY - timedelta(days=40))    # vencido
    assert [s.id for s in app.pagos.proximos_vencimientos(7, hoy=HOY)] == [socio.id]
    assert [s.id for s in app.pagos.morosos(hoy=HOY)] == [otro.id]


def test_reportes_csv(app, socio):
    app.pagos.cobrar(socio.id, hoy=HOY)
    ruta = app.reportes.ingresos(2026, 11)
    with open(ruta, encoding="utf-8-sig") as f:
        filas = list(csv.reader(f))
    assert filas[0][0] == "Comprobante"
    assert filas[1][0] == "P-0001"
    assert filas[-1][-1] == "1100.00"
    with pytest.raises(ValueError):
        app.reportes.ingresos(2026, 13)
    assert app.reportes.asistencia(2026, 11).exists()
    assert app.reportes.morosos(date(2027, 1, 1)).exists()
