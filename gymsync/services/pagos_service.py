"""Cobros, renovaciones, comprobantes .txt y vencimientos (RF3)."""
from datetime import date, timedelta
from pathlib import Path

from gymsync.algorithms.ordenamiento import merge_sort
from gymsync.config import METODOS_PAGO
from gymsync.models import Pago, Socio
from gymsync.services.config_service import ConfigService
from gymsync.services.fechas import a_texto
from gymsync.services.socios_service import SociosService
from gymsync.storage.repositorio import Repositorio


class PagosService:
    def __init__(self, socios: SociosService, config: ConfigService,
                 repo_pagos: Repositorio, carpeta_comprobantes: Path):
        self.socios = socios
        self.config = config
        self.repo_pagos = repo_pagos
        self.carpeta_comprobantes = Path(carpeta_comprobantes)

    def _siguiente_comprobante(self) -> str:
        return f"P-{self.repo_pagos.cantidad() + 1:04d}"

    @staticmethod
    def calcular_vencimiento(socio: Socio, dias_plan: int, hoy: date,
                             desde_vencimiento: bool = True) -> date:
        """Si la membresía sigue vigente y se renueva desde el vencimiento, se suman los días
        al vencimiento actual; si no, la nueva vigencia empieza hoy (hoy cuenta como día 1)."""
        vigente = socio.fecha_vencimiento is not None and socio.fecha_vencimiento >= hoy
        if desde_vencimiento and vigente:
            return socio.fecha_vencimiento + timedelta(days=dias_plan)
        return hoy + timedelta(days=dias_plan - 1)

    def cobrar(self, id_o_cedula: str, plan: str | None = None, metodo: str = "Efectivo",
               desde_vencimiento: bool = True, hoy: date | None = None) -> tuple[Pago, Path]:
        """Registra el cobro, extiende la membresía y genera el comprobante. Devuelve (pago, ruta_txt)."""
        hoy = hoy or date.today()
        socio = self.socios.obtener(id_o_cedula)
        if not socio.activo:
            raise ValueError(f"El socio {socio.id} está dado de baja; reactívelo antes de cobrar.")
        if metodo not in METODOS_PAGO:
            raise ValueError(f"Método de pago inválido. Opciones: {', '.join(METODOS_PAGO)}.")
        plan_obj = self.config.obtener_plan(plan or socio.plan)
        if not plan_obj.cubre(socio.disciplina):
            raise ValueError(f"El plan '{plan_obj.nombre}' no cubre la disciplina {socio.disciplina}.")

        nuevo_vencimiento = self.calcular_vencimiento(socio, plan_obj.dias, hoy, desde_vencimiento)
        pago = Pago(self._siguiente_comprobante(), socio.id, plan_obj.nombre,
                    plan_obj.precio, hoy, metodo, nuevo_vencimiento)
        self.repo_pagos.agregar(pago)

        socio.plan = plan_obj.nombre
        socio.fecha_vencimiento = nuevo_vencimiento
        self.socios.guardar_cambios(socio)
        return pago, self.generar_comprobante(pago, socio)

    def generar_comprobante(self, pago: Pago, socio: Socio) -> Path:
        self.carpeta_comprobantes.mkdir(parents=True, exist_ok=True)
        ruta = self.carpeta_comprobantes / f"{pago.comprobante}.txt"
        lineas = [
            "=" * 40,
            "           GYMSYNC - COMPROBANTE",
            "=" * 40,
            f"Comprobante : {pago.comprobante}",
            f"Fecha       : {a_texto(pago.fecha)}",
            f"Socio       : {socio.nombre} ({socio.id})",
            f"Cédula      : {socio.cedula}",
            f"Plan        : {pago.plan}",
            f"Vigente hasta: {a_texto(pago.vigente_hasta)}",
            f"Método      : {pago.metodo}",
            "-" * 40,
            f"TOTAL       : C$ {pago.monto:,.2f}",
            "=" * 40,
            "¡Gracias por entrenar con nosotros!",
        ]
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        return ruta

    def historial(self, id_o_cedula: str | None = None) -> list[Pago]:
        """Pagos más recientes primero; opcionalmente solo los de un socio."""
        pagos = self.repo_pagos.todos()
        if id_o_cedula:
            socio_id = self.socios.obtener(id_o_cedula).id
            pagos = [p for p in pagos if p.socio_id == socio_id]
        return merge_sort(pagos, key=lambda p: (p.fecha, p.comprobante), reverso=True)

    def proximos_vencimientos(self, dias: int = 7, hoy: date | None = None) -> list[Socio]:
        """Socios activos cuya membresía vence entre hoy y hoy + dias, el más cercano primero."""
        hoy = hoy or date.today()
        limite = hoy + timedelta(days=dias)
        candidatos = [s for s in self.socios.repo.todos()
                      if s.activo and s.fecha_vencimiento and hoy <= s.fecha_vencimiento <= limite]
        return merge_sort(candidatos, key=lambda s: s.fecha_vencimiento)

    def morosos(self, hoy: date | None = None) -> list[Socio]:
        """Socios activos con la membresía vencida, del más atrasado al menos atrasado."""
        hoy = hoy or date.today()
        vencidos = [s for s in self.socios.repo.todos()
                    if s.activo and s.fecha_vencimiento and s.fecha_vencimiento < hoy]
        return merge_sort(vencidos, key=lambda s: s.fecha_vencimiento)
