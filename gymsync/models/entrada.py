from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class Entrada:
    """Registro de un intento de acceso en el molinete virtual."""
    socio_id: str
    fecha_hora: datetime
    disciplina: str
    resultado: str  # VERDE / AMARILLA / ROJA

    def to_dict(self) -> dict:
        return asdict(self)
