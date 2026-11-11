"""Reportes mensuales en .csv (RF6)."""
import csv
from datetime import date
from pathlib import Path

from gymsync.algorithms.ordenamiento import merge_sort
from gymsync.config import ROJA
from gymsync.services.fechas import a_texto
from gymsync.services.pagos_service import PagosService
from gymsync.services.socios_service import SociosService
from gymsync.storage.repositorio import Repositorio


class ReportesService:
    def __init__(self, socios: SociosService, pagos: PagosService,
                 repo_entradas: Repositorio, carpeta_reportes: Path):
        self.socios = socios
        self.pagos = pagos
        self.repo_entradas = repo_entradas
        self.carpeta = Path(carpeta_reportes)

    @staticmethod
    def _validar_mes(anio: int, mes: int) -> None:
        if not 1 <= mes <= 12 or not 2000 <= anio <= 2100:
            raise ValueError("Mes o año inválido.")

    def _escribir_csv(self, nombre: str, encabezado: list[str], filas: list[list]) -> Path:
        self.carpeta.mkdir(parents=True, exist_ok=True)
        ruta = self.carpeta / nombre
        # utf-8-sig para que Excel muestre bien las tildes
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(encabezado)
            escritor.writerows(filas)
        return ruta

    def ingresos(self, anio: int, mes: int) -> Path:
        self._validar_mes(anio, mes)
        pagos = [p for p in self.pagos.repo_pagos.todos()
                 if p.fecha.year == anio and p.fecha.month == mes]
        pagos = merge_sort(pagos, key=lambda p: (p.fecha, p.comprobante))
        filas = []
        for p in pagos:
            socio = self.socios.buscar_por_id(p.socio_id)
            filas.append([p.comprobante, a_texto(p.fecha), p.socio_id,
                          socio.nombre if socio else "-", p.plan, p.metodo, f"{p.monto:.2f}"])
        filas.append(["", "", "", "", "", "TOTAL", f"{sum(p.monto for p in pagos):.2f}"])
        return self._escribir_csv(f"ingresos_{anio}-{mes:02d}.csv",
                                  ["Comprobante", "Fecha", "ID", "Socio", "Plan", "Método", "Monto C$"],
                                  filas)

    def asistencia(self, anio: int, mes: int) -> Path:
        """Entradas permitidas por socio en el mes, de mayor a menor."""
        self._validar_mes(anio, mes)
        conteo: dict[str, int] = {}
        for e in self.repo_entradas.todos():
            if e.fecha_hora.year == anio and e.fecha_hora.month == mes and e.resultado != ROJA:
                conteo[e.socio_id] = conteo.get(e.socio_id, 0) + 1
        orden = merge_sort(list(conteo.items()), key=lambda par: par[1], reverso=True)
        filas = []
        for socio_id, visitas in orden:
            socio = self.socios.buscar_por_id(socio_id)
            filas.append([socio_id, socio.nombre if socio else "-",
                          socio.disciplina if socio else "-", visitas])
        return self._escribir_csv(f"asistencia_{anio}-{mes:02d}.csv",
                                  ["ID", "Socio", "Disciplina", "Visitas"], filas)

    def morosos(self, hoy: date | None = None) -> Path:
        hoy = hoy or date.today()
        filas = [[s.id, s.nombre, s.telefono, s.plan, a_texto(s.fecha_vencimiento),
                  (hoy - s.fecha_vencimiento).days] for s in self.pagos.morosos(hoy)]
        return self._escribir_csv(f"morosos_{hoy.isoformat()}.csv",
                                  ["ID", "Socio", "Teléfono", "Plan", "Venció", "Días de atraso"],
                                  filas)
