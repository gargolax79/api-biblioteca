import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException

from datos import (
    calcular_proximo_id,
    cargar_libros,
    guardar_libros,
    leer_texto_archivo,
)
from schemas import Libro, LibroConId, LibroParcial

RUTA_LOG = Path(__file__).parent / "api.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    filename=RUTA_LOG,
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

app = FastAPI()

libros = cargar_libros()
proximo_id = calcular_proximo_id(libros)
ultimo_estado_archivo = leer_texto_archivo()


def sincronizar_datos() -> None:
    """Recarga los datos si el archivo cambió externamente en el disco."""
    global libros, proximo_id, ultimo_estado_archivo
    estado_actual = leer_texto_archivo()
    if estado_actual != ultimo_estado_archivo:
        libros = cargar_libros()
        proximo_id = calcular_proximo_id(libros)
        ultimo_estado_archivo = estado_actual


def persistir_cambios() -> None:
    """Guarda la lista de libros en el archivo y actualiza el estado conocido."""
    global ultimo_estado_archivo
    guardar_libros(libros)
    ultimo_estado_archivo = leer_texto_archivo()


def buscar_libro(id: int):
    """Busca un libro por su id o lanza 404 si no existe."""
    sincronizar_datos()
    for libro in libros:
        if libro["id"] == id:
            return libro
    logger.warning("Libro con id %s no existe", id)
    raise HTTPException(status_code=404, detail=f"No existe el libro con id {id}")


def existe_libro(titulo: str, autor: str) -> bool:
    """Verifica si ya existe un libro con el mismo título y autor."""
    titulo_buscado = titulo.strip().lower()
    autor_buscado = autor.strip().lower()
    return any(
        libro["titulo"].strip().lower() == titulo_buscado
        and libro["autor"].strip().lower() == autor_buscado
        for libro in libros
    )


@app.get("/", summary="Inicio")
def inicio():
    """Devuelve el mensaje de bienvenida de la API."""
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroConId], summary="Listar libros")
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = 0,
    limite: int = 100,
):
    """Lista libros ordenados por id, aplicando filtros opcionales y paginación."""
    sincronizar_datos()
    resultado = sorted(libros, key=lambda libro: libro["id"])

    if autor is not None:
        autor_buscado = autor.strip().lower()
        resultado = [
            libro
            for libro in resultado
            if libro["autor"].strip().lower() == autor_buscado
        ]

    if disponible is not None:
        resultado = [libro for libro in resultado if libro["disponible"] == disponible]

    return resultado[desde : desde + limite]


@app.get(
    "/libros/buscar",
    response_model=list[LibroConId],
    summary="Buscar libros por texto",
)
def buscar_libros(texto: str):
    """Busca libros cuyo título o autor contenga el texto indicado."""
    sincronizar_datos()
    buscado = texto.strip().lower()
    libros_ordenados = sorted(libros, key=lambda libro: libro["id"])
    return [
        libro
        for libro in libros_ordenados
        if buscado in libro["titulo"].lower() or buscado in libro["autor"].lower()
    ]


@app.get(
    "/libros/estadisticas",
    summary="Estadísticas de la biblioteca",
)
def obtener_estadisticas():
    """Devuelve el total de libros, cuántos están disponibles y cuántos prestados."""
    sincronizar_datos()
    total = len(libros)
    disponibles = sum(1 for libro in libros if libro["disponible"])
    prestados = total - disponibles
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": prestados,
    }


@app.post(
    "/libros",
    status_code=201,
    response_model=LibroConId,
    summary="Crear un libro",
)
def crear_libro(libro: Libro):
    """Crea un nuevo libro, le asigna un id único y lo guarda en archivo."""
    global proximo_id
    sincronizar_datos()
    if existe_libro(libro.titulo, libro.autor):
        logger.warning("Intento de crear libro duplicado: %s", libro.titulo)
        raise HTTPException(
            status_code=409,
            detail="Ya existe un libro con el mismo título y autor",
        )
    nuevo = {"id": proximo_id, **libro.model_dump()}
    proximo_id += 1
    libros.append(nuevo)
    persistir_cambios()
    logger.info("Libro %s creado: %s", nuevo["id"], nuevo["titulo"])
    return nuevo


@app.get(
    "/libros/{id}",
    response_model=LibroConId,
    summary="Obtener un libro por id",
)
def obtener_libro(id: int):
    """Devuelve el libro con ese id o 404 si no existe."""
    return buscar_libro(id)


@app.put(
    "/libros/{id}",
    response_model=LibroConId,
    summary="Reemplazar un libro por id",
)
def reemplazar_libro(id: int, datos: Libro):
    """Reemplaza todos los campos del libro con ese id y guarda los cambios."""
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    persistir_cambios()
    logger.info("Libro %s reemplazado", id)
    return libro


@app.patch(
    "/libros/{id}",
    response_model=LibroConId,
    summary="Actualizar parcialmente un libro por id",
)
def actualizar_libro(id: int, datos: LibroParcial):
    """Actualiza solo los campos enviados del libro con ese id y guarda."""
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    libro.update(cambios)
    persistir_cambios()
    logger.info("Libro %s actualizado parcialmente", id)
    return libro


@app.delete(
    "/libros/{id}",
    status_code=204,
    summary="Eliminar un libro por id",
)
def borrar_libro(id: int):
    """Elimina el libro con ese id y actualiza el archivo. Devuelve 204."""
    libro = buscar_libro(id)
    libros.remove(libro)
    persistir_cambios()
    logger.info("Libro %s eliminado", id)


@app.post(
    "/libros/{id}/prestar",
    response_model=LibroConId,
    summary="Prestar un libro por id",
)
def prestar_libro(id: int):
    """Marca un libro como no disponible (prestado) o devuelve 409 si ya lo estaba."""
    libro = buscar_libro(id)
    if not libro["disponible"]:
        logger.warning("El libro %s ya estaba prestado", id)
        raise HTTPException(
            status_code=409,
            detail="El libro ya está prestado",
        )
    libro["disponible"] = False
    persistir_cambios()
    logger.info("Libro %s prestado", id)
    return libro


@app.post(
    "/libros/{id}/devolver",
    response_model=LibroConId,
    summary="Devolver un libro por id",
)
def devolver_libro(id: int):
    """Marca un libro como disponible o devuelve 409 si ya estaba disponible."""
    libro = buscar_libro(id)
    if libro["disponible"]:
        logger.warning("El libro %s ya estaba disponible", id)
        raise HTTPException(
            status_code=409,
            detail="El libro ya estaba disponible",
        )
    libro["disponible"] = True
    persistir_cambios()
    logger.info("Libro %s devuelto", id)
    return libro
