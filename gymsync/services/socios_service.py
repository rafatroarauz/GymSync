"""Gestión de socios: alta, consulta, edición y baja (RF1)."""
from datetime import date

from gymsync.algorithms.busqueda import busqueda_binaria
from gymsync.algorithms.ordenamiento import merge_sort
from gymsync.config import UMBRAL_POR_VENCER_DIAS
from gymsync.models import Socio
from gymsync.services.config_service import ConfigService
from gymsync.services.fechas import a_fecha
from gymsync.storage.repositorio import Repositorio

CAMPOS_EDITABLES = ("nombre", "telefono", "disciplina", "plan")


class SociosService:
    def __init__(self, repo_socios: Repositorio, config: ConfigService):
        self.repo = repo_socios
        self.config = config
        self._indice_id: list[Socio] = []
        self._indice_cedula: list[Socio] = []
        self._reconstruir_indices()

    # ---------- índices ordenados para búsqueda binaria (RNF2) ----------
    def _reconstruir_indices(self) -> None:
        socios = self.repo.todos()
        self._indice_id = merge_sort(socios, key=lambda s: s.id)
        self._indice_cedula = merge_sort(socios, key=lambda s: s.cedula)

    def buscar_por_id(self, socio_id: str) -> Socio | None:
        i = busqueda_binaria(self._indice_id, socio_id.strip().upper(), key=lambda s: s.id)
        return self._indice_id[i] if i != -1 else None

    def buscar_por_cedula(self, cedula: str) -> Socio | None:
        i = busqueda_binaria(self._indice_cedula, cedula.strip().upper(), key=lambda s: s.cedula)
        return self._indice_cedula[i] if i != -1 else None

    def buscar(self, id_o_cedula: str) -> Socio | None:
        """Busca primero por ID y luego por cédula."""
        return self.buscar_por_id(id_o_cedula) or self.buscar_por_cedula(id_o_cedula)

    def obtener(self, id_o_cedula: str) -> Socio:
        socio = self.buscar(id_o_cedula)
        if socio is None:
            raise ValueError(f"No se encontró ningún socio con ID o cédula '{id_o_cedula}'.")
        return socio

    # ---------- CRUD ----------
    def _siguiente_id(self) -> str:
        numeros = [int(s.id.split("-")[1]) for s in self.repo.todos()]
        return f"A-{max(numeros, default=1000) + 1}"

    def _validar_disciplina_y_plan(self, disciplina: str, plan_nombre: str) -> None:
        if disciplina not in self.config.listar_disciplinas():
            raise ValueError(f"La disciplina '{disciplina}' no existe.")
        plan = self.config.obtener_plan(plan_nombre)
        if not plan.cubre(disciplina):
            raise ValueError(f"El plan '{plan_nombre}' no cubre la disciplina '{disciplina}'.")

    def registrar(self, cedula: str, nombre: str, telefono: str, disciplina: str,
                  plan: str, fecha_inicio=None) -> Socio:
        cedula, nombre, telefono = cedula.strip().upper(), nombre.strip(), telefono.strip()
        if not (cedula and nombre and telefono and disciplina and plan):
            raise ValueError("Cédula, nombre, teléfono, disciplina y plan son obligatorios.")
        if self.buscar_por_cedula(cedula) is not None:
            raise ValueError(f"Ya existe un socio con la cédula {cedula}.")
        self._validar_disciplina_y_plan(disciplina, plan)
        inicio = a_fecha(fecha_inicio) if fecha_inicio else date.today()
        socio = Socio(self._siguiente_id(), cedula, nombre, telefono, disciplina, plan, inicio)
        self.repo.agregar(socio)
        self._reconstruir_indices()
        return socio

    def editar(self, socio_id: str, **cambios) -> Socio:
        socio = self.obtener(socio_id)
        invalidos = [c for c in cambios if c not in CAMPOS_EDITABLES]
        if invalidos:
            raise ValueError(f"No se pueden editar los campos: {', '.join(invalidos)}.")
        cambios = {c: str(v).strip() for c, v in cambios.items() if str(v).strip()}
        disciplina = cambios.get("disciplina", socio.disciplina)
        plan = cambios.get("plan", socio.plan)
        self._validar_disciplina_y_plan(disciplina, plan)
        for campo, valor in cambios.items():
            setattr(socio, campo, valor)
        self.repo.actualizar(socio)
        self._reconstruir_indices()
        return socio

    def guardar_cambios(self, socio: Socio) -> None:
        """Persiste un socio modificado por otro servicio (por ejemplo, al renovar)."""
        self.repo.actualizar(socio)
        self._reconstruir_indices()

    def dar_de_baja(self, socio_id: str) -> Socio:
        """Baja lógica: el socio se conserva en el historial pero ya no puede entrar."""
        socio = self.obtener(socio_id)
        if not socio.activo:
            raise ValueError(f"El socio {socio.id} ya estaba dado de baja.")
        socio.activo = False
        self.guardar_cambios(socio)
        return socio

    def reactivar(self, socio_id: str) -> Socio:
        socio = self.obtener(socio_id)
        socio.activo = True
        self.guardar_cambios(socio)
        return socio

    # ---------- consultas ----------
    @staticmethod
    def estado(socio: Socio, hoy: date | None = None) -> str:
        hoy = hoy or date.today()
        if not socio.activo:
            return "Baja"
        if socio.fecha_vencimiento is None:
            return "Sin pago"
        if socio.fecha_vencimiento < hoy:
            return "Vencido"
        if (socio.fecha_vencimiento - hoy).days <= UMBRAL_POR_VENCER_DIAS:
            return "Por vencer"
        return "Activo"

    def listar(self, texto: str = "", estado: str | None = None, hoy: date | None = None) -> list[Socio]:
        """Lista ordenada por nombre, filtrando por texto (nombre/ID/cédula) y estado."""
        texto = texto.strip().lower()
        resultado = []
        for socio in self.repo.todos():
            coincide = (not texto or texto in socio.nombre.lower()
                        or texto in socio.id.lower() or texto in socio.cedula.lower())
            if coincide and (estado is None or self.estado(socio, hoy) == estado):
                resultado.append(socio)
        return merge_sort(resultado, key=lambda s: s.nombre.lower())
