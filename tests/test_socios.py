import pytest

from conftest import HOY


def test_registrar_asigna_id_consecutivo(app, socio):
    otro = app.socios.registrar("002", "Carlos", "7550", "Musculación", "Mensual Musculación")
    assert socio.id == "A-1001"
    assert otro.id == "A-1002"


def test_cedula_duplicada_es_rechazada(app, socio):
    with pytest.raises(ValueError, match="cédula"):
        app.socios.registrar(socio.cedula.lower(), "Otra", "1111", "MMA", "Mensual Combate")


@pytest.mark.parametrize("campo_vacio", ["cedula", "nombre", "telefono"])
def test_campos_obligatorios(app, campo_vacio):
    datos = {"cedula": "003", "nombre": "Luis", "telefono": "7650"}
    datos[campo_vacio] = "   "
    with pytest.raises(ValueError, match="obligatorios"):
        app.socios.registrar(**datos, disciplina="BJJ", plan="Mensual Combate")


def test_plan_que_no_cubre_la_disciplina(app):
    with pytest.raises(ValueError, match="no cubre"):
        app.socios.registrar("004", "Sofía", "8277", "MMA", "Mensual Musculación")


def test_fecha_invalida(app):
    with pytest.raises(ValueError, match="dd/mm/aaaa"):
        app.socios.registrar("005", "Jorge", "8891", "BJJ", "Mensual Combate", "31-02-2026")


def test_buscar_por_id_o_cedula(app, socio):
    assert app.socios.buscar("a-1001") is socio
    assert app.socios.buscar("001-170594-0012a") is socio
    assert app.socios.buscar("no-existe") is None


def test_editar_y_baja(app, socio):
    app.socios.editar(socio.id, telefono="8000-0000", disciplina="BJJ")
    assert app.socios.buscar(socio.id).telefono == "8000-0000"
    with pytest.raises(ValueError):
        app.socios.editar(socio.id, cedula="999")  # la cédula no es editable

    app.socios.dar_de_baja(socio.id)
    assert app.socios.estado(socio, HOY) == "Baja"
    with pytest.raises(ValueError, match="ya estaba"):
        app.socios.dar_de_baja(socio.id)


def test_listar_ordena_por_nombre_y_filtra(app, socio):
    app.socios.registrar("006", "Ana Castillo", "8844", "BJJ", "Mensual Combate")
    nombres = [s.nombre for s in app.socios.listar()]
    assert nombres == ["Ana Castillo", "María López"]
    assert [s.nombre for s in app.socios.listar("castillo")] == ["Ana Castillo"]
    assert len(app.socios.listar(estado="Sin pago", hoy=HOY)) == 2
