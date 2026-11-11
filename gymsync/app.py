"""Ensambla repositorios y servicios. Recibir la carpeta base permite que las pruebas
usen una carpeta temporal sin tocar los datos reales."""
from dataclasses import dataclass
from pathlib import Path

from gymsync import config
from gymsync.services.acceso_service import AccesoService
from gymsync.services.config_service import ConfigService
from gymsync.services.pagos_service import PagosService
from gymsync.services.reportes_service import ReportesService
from gymsync.services.socios_service import SociosService
from gymsync.storage import respaldo
from gymsync.storage.repositorio import Repositorio


@dataclass
class App:
    base: Path
    config: ConfigService
    socios: SociosService
    acceso: AccesoService
    pagos: PagosService
    reportes: ReportesService

    @property
    def carpeta_datos(self) -> Path:
        return self.base / config.CARPETA_DATOS

    def respaldar(self) -> Path:
        return respaldo.respaldar(self.carpeta_datos, self.base / config.CARPETA_RESPALDOS)


def crear_app(base: Path | None = None) -> App:
    base = Path(base or config.BASE_DIR)
    datos = base / config.CARPETA_DATOS

    repo_planes = Repositorio(datos / config.ARCHIVO_PLANES, clave="nombre")
    repo_disciplinas = Repositorio(datos / config.ARCHIVO_DISCIPLINAS, clave="nombre")
    repo_socios = Repositorio(datos / config.ARCHIVO_SOCIOS, clave="id")
    repo_pagos = Repositorio(datos / config.ARCHIVO_PAGOS, clave="comprobante")
    repo_entradas = Repositorio(datos / config.ARCHIVO_ENTRADAS, clave="fecha_hora")

    config_srv = ConfigService(repo_planes, repo_disciplinas)
    config_srv.sembrar_por_defecto()
    socios = SociosService(repo_socios, config_srv)
    acceso = AccesoService(socios, config_srv, repo_entradas)
    pagos = PagosService(socios, config_srv, repo_pagos, base / config.CARPETA_COMPROBANTES)
    reportes = ReportesService(socios, pagos, repo_entradas, base / config.CARPETA_REPORTES)
    return App(base, config_srv, socios, acceso, pagos, reportes)
