from datetime import date

import pytest

from gymsync.app import crear_app

HOY = date(2026, 11, 11)


@pytest.fixture
def app(tmp_path):
    """Aplicación completa sobre una carpeta temporal (no toca data/ real)."""
    return crear_app(tmp_path)


@pytest.fixture
def socio(app):
    """Socio de MMA con plan Mensual Combate, aún sin pagar."""
    return app.socios.registrar("001-170594-0012A", "María López", "8888-1204",
                                "MMA", "Mensual Combate", HOY)
