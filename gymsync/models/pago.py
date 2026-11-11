from dataclasses import asdict, dataclass
from datetime import date


@dataclass
class Pago:
    """Cobro o renovación de una membresía."""
    comprobante: str
    socio_id: str
    plan: str
    monto: float
    fecha: date
    metodo: str
    vigente_hasta: date

    def to_dict(self) -> dict:
        return asdict(self)
