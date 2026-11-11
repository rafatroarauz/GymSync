"""Funciones auxiliares para convertir y mostrar fechas."""
from datetime import date, datetime

from gymsync.config import FORMATO_FECHA


def a_fecha(valor) -> date:
    """Acepta un date o un texto 'dd/mm/aaaa' y devuelve un date."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), FORMATO_FECHA).date()
    except ValueError:
        raise ValueError(f"Fecha inválida '{valor}'. Use el formato dd/mm/aaaa.") from None


def a_texto(fecha: date | None) -> str:
    return fecha.strftime(FORMATO_FECHA) if fecha else "-"
