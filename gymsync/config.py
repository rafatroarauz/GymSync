"""Configuración global de GymSync: rutas de archivos y constantes de negocio."""
from pathlib import Path

# Carpeta raíz del proyecto (ProyectoFinal/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Nombres de los archivos binarios (RNF1: persistencia local)
ARCHIVO_SOCIOS = "socios.dat"
ARCHIVO_PLANES = "planes.dat"
ARCHIVO_DISCIPLINAS = "disciplinas.dat"
ARCHIVO_PAGOS = "pagos.dat"
ARCHIVO_ENTRADAS = "entradas.dat"

# Subcarpetas generadas automáticamente
CARPETA_DATOS = "data"
CARPETA_COMPROBANTES = "comprobantes"
CARPETA_REPORTES = "reportes"
CARPETA_RESPALDOS = "backups"

# Reglas de negocio (RF2)
UMBRAL_POR_VENCER_DIAS = 3

# Banderas del molinete virtual
VERDE = "VERDE"
AMARILLA = "AMARILLA"
ROJA = "ROJA"

METODOS_PAGO = ("Efectivo", "Tarjeta", "Transferencia")
FORMATO_FECHA = "%d/%m/%Y"
