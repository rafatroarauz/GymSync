"""Molinete virtual: valida el acceso y registra cada entrada (RF2)."""
from dataclasses import dataclass
from datetime import date, datetime

from gymsync.algorithms.ordenamiento import merge_sort
from gymsync.config import AMARILLA, ROJA, UMBRAL_POR_VENCER_DIAS, VERDE
from gymsync.models import Entrada, Socio
from gymsync.services.config_service import ConfigService
from gymsync.services.socios_service import SociosService
from gymsync.storage.repositorio import Repositorio


@dataclass
class ResultadoAcceso:
    bandera: str
    mensaje: str
    socio: Socio


class AccesoService:
    def __init__(self, socios: SociosService, config: ConfigService, repo_entradas: Repositorio):
        self.socios = socios
        self.config = config
        self.repo_entradas = repo_entradas

    def evaluar(self, socio: Socio, disciplina: str, hoy: date) -> tuple[str, str]:
        """Función pura: decide la bandera sin registrar nada."""
        if not socio.activo:
            return ROJA, "Socio dado de baja."
        if socio.fecha_vencimiento is None:
            return ROJA, "Sin membresía pagada."
        if socio.fecha_vencimiento < hoy:
            dias = (hoy - socio.fecha_vencimiento).days
            return ROJA, f"Membresía vencida hace {dias} día(s)."
        plan = self.config.obtener_plan(socio.plan)
        if not plan.cubre(disciplina):
            return ROJA, f"El plan '{plan.nombre}' no cubre {disciplina}."
        restantes = (socio.fecha_vencimiento - hoy).days
        if restantes <= UMBRAL_POR_VENCER_DIAS:
            return AMARILLA, f"Acceso permitido. Vence en {restantes} día(s): recordar renovar."
        return VERDE, "Acceso permitido."

    def validar(self, id_o_cedula: str, disciplina: str | None = None,
                ahora: datetime | None = None) -> ResultadoAcceso:
        """Busca al socio (búsqueda binaria), decide la bandera y registra la entrada."""
        if not id_o_cedula or not id_o_cedula.strip():
            raise ValueError("Ingrese un ID o una cédula.")
        socio = self.socios.obtener(id_o_cedula)
        ahora = ahora or datetime.now()
        disciplina = disciplina or socio.disciplina
        bandera, mensaje = self.evaluar(socio, disciplina, ahora.date())
        self.repo_entradas.anexar(Entrada(socio.id, ahora, disciplina, bandera))
        return ResultadoAcceso(bandera, mensaje, socio)

    def entradas_del_dia(self, dia: date | None = None) -> list[Entrada]:
        dia = dia or date.today()
        entradas = self.repo_entradas.filtrar(lambda e: e.fecha_hora.date() == dia)
        return merge_sort(entradas, key=lambda e: e.fecha_hora, reverso=True)
