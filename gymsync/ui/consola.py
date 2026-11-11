"""Interfaz de consola (temporal hasta la GUI en Tkinter de la Etapa 5).
Cada opción del menú es un procedimiento que solo llama a los servicios."""
import os
from datetime import date

from gymsync import config, datos_demo
from gymsync.app import App
from gymsync.services.fechas import a_texto
from gymsync.storage.archivo_binario import ErrorArchivo

# Colores ANSI para el molinete (RNF3)
COLOR = {config.VERDE: "\033[92m", config.AMARILLA: "\033[93m", config.ROJA: "\033[91m"}
RESET, NEGRITA = "\033[0m", "\033[1m"


# ---------------- utilidades de entrada/salida ----------------
def titulo(texto: str) -> None:
    print(f"\n{NEGRITA}{'=' * 50}\n  {texto}\n{'=' * 50}{RESET}")


def pedir(mensaje: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(f"{mensaje}: ").strip()
        if valor or not obligatorio:
            return valor
        print("  Este campo es obligatorio.")


def elegir(mensaje: str, opciones: list[str]) -> str:
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    while True:
        valor = input(f"{mensaje} (1-{len(opciones)}): ").strip()
        if valor.isdigit() and 1 <= int(valor) <= len(opciones):
            return opciones[int(valor) - 1]
        print("  Opción inválida.")


def confirmar(mensaje: str) -> bool:
    return input(f"{mensaje} (s/n): ").strip().lower() == "s"


def pausa() -> None:
    input("\nPresione Enter para continuar...")


def ok(mensaje: str) -> None:
    print(f"{COLOR[config.VERDE]}✔ {mensaje}{RESET}")


def error(mensaje: str) -> None:
    print(f"{COLOR[config.ROJA]}✘ {mensaje}{RESET}")


def imprimir_tabla(encabezado: list[str], filas: list[list]) -> None:
    if not filas:
        print("  (sin registros)")
        return
    anchos = [max(len(str(x)) for x in col) for col in zip(encabezado, *filas)]
    linea = "  ".join(f"{{:<{a}}}" for a in anchos)
    print(NEGRITA + linea.format(*encabezado) + RESET)
    print("-" * (sum(anchos) + 2 * (len(anchos) - 1)))
    for fila in filas:
        print(linea.format(*[str(x) for x in fila]))


def filas_socios(app: App, socios) -> list[list]:
    return [[s.id, s.nombre, s.cedula, s.telefono, s.disciplina, s.plan,
             a_texto(s.fecha_vencimiento), app.socios.estado(s)] for s in socios]


ENCABEZADO_SOCIOS = ["ID", "Nombre", "Cédula", "Teléfono", "Disciplina", "Plan", "Vence", "Estado"]


# ---------------- 1. Socios (RF1) ----------------
def menu_socios(app: App) -> None:
    opciones = {
        "1": ("Registrar socio", registrar_socio),
        "2": ("Buscar socio por ID o cédula", consultar_socio),
        "3": ("Listar / filtrar socios", listar_socios),
        "4": ("Editar socio", editar_socio),
        "5": ("Dar de baja", baja_socio),
    }
    submenu(app, "SOCIOS", opciones)


def registrar_socio(app: App) -> None:
    cedula = pedir("Cédula (ej. 001-170594-0012A)")
    nombre = pedir("Nombre completo")
    telefono = pedir("Teléfono")
    disciplina = elegir("Disciplina", app.config.listar_disciplinas())
    planes = [p.nombre for p in app.config.listar_planes() if p.cubre(disciplina)]
    plan = elegir("Plan", planes)
    socio = app.socios.registrar(cedula, nombre, telefono, disciplina, plan)
    ok(f"Socio registrado con ID {socio.id}.")
    if confirmar("¿Cobrar la primera membresía ahora?"):
        cobrar_membresia(app, socio.id)


def consultar_socio(app: App) -> None:
    socio = app.socios.obtener(pedir("ID o cédula"))
    imprimir_tabla(ENCABEZADO_SOCIOS, filas_socios(app, [socio]))
    pagos = app.pagos.historial(socio.id)[:5]
    print("\nÚltimos pagos:")
    imprimir_tabla(["Comprobante", "Fecha", "Plan", "Monto"],
                   [[p.comprobante, a_texto(p.fecha), p.plan, f"C$ {p.monto:,.2f}"] for p in pagos])


def listar_socios(app: App) -> None:
    texto = pedir("Buscar (nombre/ID/cédula, Enter = todos)", obligatorio=False)
    estado = elegir("Estado", ["Todos", "Activo", "Por vencer", "Vencido", "Sin pago", "Baja"])
    socios = app.socios.listar(texto, None if estado == "Todos" else estado)
    imprimir_tabla(ENCABEZADO_SOCIOS, filas_socios(app, socios))
    print(f"\nMostrando {len(socios)} de {app.socios.repo.cantidad()} socios.")


def editar_socio(app: App) -> None:
    socio = app.socios.obtener(pedir("ID o cédula del socio a editar"))
    print("Deje en blanco lo que no quiera cambiar.")
    cambios = {
        "nombre": pedir(f"Nombre [{socio.nombre}]", obligatorio=False),
        "telefono": pedir(f"Teléfono [{socio.telefono}]", obligatorio=False),
    }
    if confirmar(f"¿Cambiar disciplina/plan? (actual: {socio.disciplina} / {socio.plan})"):
        cambios["disciplina"] = elegir("Disciplina", app.config.listar_disciplinas())
        cambios["plan"] = elegir("Plan", [p.nombre for p in app.config.listar_planes()
                                          if p.cubre(cambios["disciplina"])])
    app.socios.editar(socio.id, **cambios)
    ok("Socio actualizado.")


def baja_socio(app: App) -> None:
    socio = app.socios.obtener(pedir("ID o cédula"))
    if confirmar(f"¿Dar de baja a {socio.nombre} ({socio.id})?"):
        app.socios.dar_de_baja(socio.id)
        ok("Socio dado de baja.")


# ---------------- 2. Molinete virtual (RF2) ----------------
def menu_molinete(app: App) -> None:
    titulo("MOLINETE VIRTUAL  (Enter vacío para salir)")
    while True:
        dato = input("\nID o cédula del socio: ").strip()
        if not dato:
            return
        try:
            r = app.acceso.validar(dato)
            print(f"{COLOR[r.bandera]}{NEGRITA}  ■■■ {r.bandera} ■■■  {r.socio.nombre} "
                  f"({r.socio.id}) - {r.mensaje}{RESET}")
        except ValueError as e:
            error(str(e))
        entradas = app.acceso.entradas_del_dia()
        print(f"Entradas de hoy: {len(entradas)}")


# ---------------- 3. Pagos (RF3) ----------------
def menu_pagos(app: App) -> None:
    opciones = {
        "1": ("Cobrar / renovar membresía", lambda a: cobrar_membresia(a)),
        "2": ("Historial de pagos", historial_pagos),
        "3": ("Próximos vencimientos (7 días)", proximos_vencimientos),
        "4": ("Morosos", ver_morosos),
    }
    submenu(app, "PAGOS Y VENCIMIENTOS", opciones)


def cobrar_membresia(app: App, socio_id: str | None = None) -> None:
    socio = app.socios.obtener(socio_id or pedir("ID o cédula"))
    print(f"Socio: {socio.nombre} - plan actual: {socio.plan} - vence: {a_texto(socio.fecha_vencimiento)}")
    planes = [p for p in app.config.listar_planes() if p.cubre(socio.disciplina)]
    nombre_plan = elegir("Plan", [f"{p.nombre} - C$ {p.precio:,.2f} ({p.dias} días)" for p in planes])
    plan = planes[[f"{p.nombre} - C$ {p.precio:,.2f} ({p.dias} días)" for p in planes].index(nombre_plan)]
    metodo = elegir("Método de pago", list(config.METODOS_PAGO))
    desde_venc = confirmar("¿Renovar desde el vencimiento actual?")
    pago, ruta = app.pagos.cobrar(socio.id, plan.nombre, metodo, desde_venc)
    ok(f"Pago {pago.comprobante} registrado. Vigente hasta {a_texto(pago.vigente_hasta)}.")
    print(f"  Comprobante: {ruta}")


def historial_pagos(app: App) -> None:
    dato = pedir("ID o cédula (Enter = todos)", obligatorio=False)
    pagos = app.pagos.historial(dato or None)[:20]
    imprimir_tabla(["Comprobante", "Socio", "Plan", "Monto", "Fecha", "Método"],
                   [[p.comprobante, p.socio_id, p.plan, f"C$ {p.monto:,.2f}",
                     a_texto(p.fecha), p.metodo] for p in pagos])


def proximos_vencimientos(app: App) -> None:
    hoy = date.today()
    socios = app.pagos.proximos_vencimientos(7)
    imprimir_tabla(["Vence", "Faltan", "ID", "Socio", "Teléfono", "Plan"],
                   [[a_texto(s.fecha_vencimiento), f"{(s.fecha_vencimiento - hoy).days} días",
                     s.id, s.nombre, s.telefono, s.plan] for s in socios])


def ver_morosos(app: App) -> None:
    hoy = date.today()
    imprimir_tabla(["ID", "Socio", "Teléfono", "Venció", "Atraso"],
                   [[s.id, s.nombre, s.telefono, a_texto(s.fecha_vencimiento),
                     f"{(hoy - s.fecha_vencimiento).days} días"] for s in app.pagos.morosos()])


# ---------------- 4. Reportes (RF6) ----------------
def menu_reportes(app: App) -> None:
    titulo("REPORTES .CSV")
    hoy = date.today()
    tipo = elegir("Reporte", ["Ingresos del mes", "Asistencia del mes", "Morosos a hoy"])
    if tipo == "Morosos a hoy":
        ruta = app.reportes.morosos()
    else:
        texto = pedir(f"Mes y año (mm/aaaa) [Enter = {hoy.month:02d}/{hoy.year}]", obligatorio=False)
        mes, anio = (hoy.month, hoy.year)
        if texto:
            try:
                mes, anio = (int(x) for x in texto.split("/"))
            except ValueError:
                raise ValueError("Formato inválido. Use mm/aaaa.") from None
        ruta = (app.reportes.ingresos if tipo.startswith("Ingresos") else app.reportes.asistencia)(anio, mes)
    ok(f"Reporte exportado: {ruta}")


# ---------------- 5. Configuración y respaldo (RF7) ----------------
def menu_config(app: App) -> None:
    opciones = {
        "1": ("Ver planes y disciplinas", ver_planes),
        "2": ("Agregar disciplina", lambda a: (a.config.agregar_disciplina(pedir("Nombre")), ok("Disciplina agregada."))),
        "3": ("Agregar plan", agregar_plan),
        "4": ("Respaldar archivos de datos", lambda a: ok(f"Respaldo creado en {a.respaldar()}")),
        "5": ("Cargar datos de ejemplo (demo)", lambda a: ok(f"{datos_demo.cargar(a)} socios de ejemplo agregados.")),
    }
    submenu(app, "CONFIGURACIÓN", opciones)


def ver_planes(app: App) -> None:
    imprimir_tabla(["Plan", "Días", "Precio", "Disciplinas"],
                   [[p.nombre, p.dias, f"C$ {p.precio:,.2f}", ", ".join(p.disciplinas)]
                    for p in app.config.listar_planes()])


def agregar_plan(app: App) -> None:
    nombre = pedir("Nombre del plan")
    try:
        dias = int(pedir("Duración en días"))
        precio = float(pedir("Precio C$"))
    except ValueError:
        raise ValueError("Días y precio deben ser numéricos.") from None
    disciplinas = []
    for d in app.config.listar_disciplinas():
        if confirmar(f"  ¿Incluye {d}?"):
            disciplinas.append(d)
    app.config.agregar_plan(nombre, dias, precio, disciplinas)
    ok("Plan agregado.")


# ---------------- menú principal ----------------
def submenu(app: App, nombre: str, opciones: dict) -> None:
    while True:
        titulo(nombre)
        for clave, (texto, _) in opciones.items():
            print(f"  {clave}. {texto}")
        print("  0. Volver")
        eleccion = input("Opción: ").strip()
        if eleccion == "0":
            return
        if eleccion not in opciones:
            error("Opción inválida.")
            continue
        ejecutar_opcion(app, opciones[eleccion][1])
        pausa()


def ejecutar_opcion(app: App, funcion) -> None:
    """Punto único de manejo de errores: la UI nunca se cae por un dato mal ingresado."""
    try:
        funcion(app)
    except (ValueError, ErrorArchivo) as e:
        error(str(e))
    except KeyboardInterrupt:
        print("\nOperación cancelada.")


def menu_principal(app: App) -> None:
    os.system("")  # activa los colores ANSI en la consola de Windows
    opciones = {
        "1": ("Socios", menu_socios),
        "2": ("Molinete virtual (registrar entrada)", menu_molinete),
        "3": ("Pagos y vencimientos", menu_pagos),
        "4": ("Reportes .csv", menu_reportes),
        "5": ("Configuración y respaldo", menu_config),
    }
    while True:
        titulo(f"GYMSYNC - {a_texto(date.today())}")
        for clave, (texto, _) in opciones.items():
            print(f"  {clave}. {texto}")
        print("  0. Salir")
        eleccion = input("Opción: ").strip()
        if eleccion == "0":
            print("¡Hasta luego!")
            return
        if eleccion in opciones:
            ejecutar_opcion(app, opciones[eleccion][1])
        else:
            error("Opción inválida.")
