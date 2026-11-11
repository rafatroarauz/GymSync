"""Planes y disciplinas (RF7)."""
from gymsync.models import Disciplina, Plan
from gymsync.storage.repositorio import Repositorio

DISCIPLINAS_POR_DEFECTO = ["Musculación", "MMA", "BJJ", "Kickboxing"]

PLANES_POR_DEFECTO = [
    Plan("Pase diario", 1, 150.0, list(DISCIPLINAS_POR_DEFECTO)),
    Plan("Mensual Musculación", 30, 900.0, ["Musculación"]),
    Plan("Mensual Combate", 30, 1100.0, ["MMA", "BJJ", "Kickboxing"]),
    Plan("Trimestral Full", 90, 2300.0, list(DISCIPLINAS_POR_DEFECTO)),
]


class ConfigService:
    def __init__(self, repo_planes: Repositorio, repo_disciplinas: Repositorio):
        self.repo_planes = repo_planes
        self.repo_disciplinas = repo_disciplinas

    def sembrar_por_defecto(self) -> None:
        """Carga planes y disciplinas iniciales solo si los archivos están vacíos."""
        if self.repo_disciplinas.cantidad() == 0:
            for nombre in DISCIPLINAS_POR_DEFECTO:
                self.repo_disciplinas.agregar(Disciplina(nombre))
        if self.repo_planes.cantidad() == 0:
            for plan in PLANES_POR_DEFECTO:
                self.repo_planes.agregar(Plan(plan.nombre, plan.dias, plan.precio, list(plan.disciplinas)))

    def listar_planes(self) -> list[Plan]:
        return self.repo_planes.todos()

    def listar_disciplinas(self) -> list[str]:
        return [d.nombre for d in self.repo_disciplinas.todos()]

    def obtener_plan(self, nombre: str) -> Plan:
        plan = self.repo_planes.obtener(nombre)
        if plan is None:
            raise ValueError(f"El plan '{nombre}' no existe.")
        return plan

    def agregar_disciplina(self, nombre: str) -> Disciplina:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la disciplina es obligatorio.")
        if nombre in self.listar_disciplinas():
            raise ValueError(f"La disciplina '{nombre}' ya existe.")
        disciplina = Disciplina(nombre)
        self.repo_disciplinas.agregar(disciplina)
        return disciplina

    def agregar_plan(self, nombre: str, dias: int, precio: float, disciplinas: list[str]) -> Plan:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del plan es obligatorio.")
        if self.repo_planes.obtener(nombre) is not None:
            raise ValueError(f"El plan '{nombre}' ya existe.")
        if dias <= 0 or precio <= 0:
            raise ValueError("Los días y el precio deben ser mayores que cero.")
        validas = self.listar_disciplinas()
        desconocidas = [d for d in disciplinas if d not in validas]
        if not disciplinas or desconocidas:
            raise ValueError(f"Disciplinas inválidas: {desconocidas or 'ninguna seleccionada'}.")
        plan = Plan(nombre, dias, precio, list(disciplinas))
        self.repo_planes.agregar(plan)
        return plan
