from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional


@dataclass
class Socio:
    """Miembro del gimnasio. fecha_vencimiento es el último día válido (inclusive);
    es None mientras el socio no haya pagado ninguna membresía."""
    id: str
    cedula: str
    nombre: str
    telefono: str
    disciplina: str
    plan: str
    fecha_inicio: date
    fecha_vencimiento: Optional[date] = None
    activo: bool = True

    def to_dict(self) -> dict:
        return asdict(self)
