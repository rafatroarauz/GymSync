"""Carga socios, pagos y entradas de ejemplo para demostrar el sistema."""
import random
from datetime import date, datetime, time, timedelta

from gymsync.app import App

SOCIOS_DEMO = [
    ("001-170594-0012A", "María López", "8888-1204", "MMA", "Mensual Combate"),
    ("001-080188-0034B", "Carlos Mejía", "7550-9231", "Musculación", "Trimestral Full"),
    ("001-220901-0021C", "Ana Castillo", "8844-1097", "BJJ", "Mensual Combate"),
    ("001-110682-0044F", "Roberto Díaz", "7712-8860", "Kickboxing", "Mensual Combate"),
    ("001-260796-0058D", "Sofía Gómez", "8277-3140", "Musculación", "Mensual Musculación"),
    ("001-030399-0011E", "Elena Ruiz", "8120-4451", "MMA", "Mensual Combate"),
    ("001-150285-0077G", "Jorge Mena", "8891-6630", "Musculación", "Mensual Musculación"),
    ("001-090993-0066H", "Luis Torres", "7650-1172", "BJJ", "Trimestral Full"),
    ("001-271290-0099J", "Nadia Pérez", "8814-3200", "Kickboxing", "Mensual Combate"),
    ("001-010101-0001K", "Diego Palma", "8333-2020", "Musculación", "Mensual Musculación"),
]

# Días desde hoy en que se pagó la última membresía (controla el estado de cada socio)
DIAS_DESDE_PAGO = [2, 10, 28, 5, 40, 26, 20, 15, 34, 29]


def cargar(app: App, hoy: date | None = None) -> int:
    """Devuelve cuántos socios se agregaron (omite los que ya existían)."""
    hoy = hoy or date.today()
    rnd = random.Random(42)
    agregados = 0
    for (cedula, nombre, tel, disciplina, plan), hace in zip(SOCIOS_DEMO, DIAS_DESDE_PAGO):
        if app.socios.buscar_por_cedula(cedula):
            continue
        fecha_pago = hoy - timedelta(days=hace)
        socio = app.socios.registrar(cedula, nombre, tel, disciplina, plan, fecha_pago)
        app.pagos.cobrar(socio.id, metodo=rnd.choice(["Efectivo", "Tarjeta", "Transferencia"]),
                         hoy=fecha_pago)
        # Entradas históricas en horarios variados (alimentan asistencia y, más adelante, horas pico)
        for d in range(hace, 0, -1):
            if rnd.random() < 0.45:
                hora = time(rnd.choice([6, 7, 9, 12, 16, 17, 18, 19]), rnd.randint(0, 59))
                app.acceso.validar(socio.id, ahora=datetime.combine(hoy - timedelta(days=d), hora))
        agregados += 1
    return agregados
