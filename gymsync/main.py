"""Punto de entrada de GymSync. Ejecutar desde ProyectoFinal/ con:  python -m gymsync.main"""
import sys

from gymsync.app import crear_app
from gymsync.storage.archivo_binario import ErrorArchivo
from gymsync.ui.consola import menu_principal


def main() -> None:
    try:
        app = crear_app()
    except ErrorArchivo as e:
        print(f"No se pudieron cargar los datos: {e}\nRestaure un respaldo desde la carpeta backups/.")
        sys.exit(1)
    try:
        menu_principal(app)
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo de GymSync.")


if __name__ == "__main__":
    main()
