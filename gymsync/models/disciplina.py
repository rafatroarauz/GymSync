from dataclasses import asdict, dataclass


@dataclass
class Disciplina:
    """Actividad que ofrece el gimnasio (MMA, BJJ, Musculación...)."""
    nombre: str

    def to_dict(self) -> dict:
        return asdict(self)
