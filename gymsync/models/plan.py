from dataclasses import asdict, dataclass, field


@dataclass
class Plan:
    """Tipo de membresía: duración en días, precio en córdobas y disciplinas que cubre."""
    nombre: str
    dias: int
    precio: float
    disciplinas: list[str] = field(default_factory=list)

    def cubre(self, disciplina: str) -> bool:
        return disciplina in self.disciplinas

    def to_dict(self) -> dict:
        return asdict(self)
