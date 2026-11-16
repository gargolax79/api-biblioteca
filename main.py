from fastapi import FastAPI, HTTPException
from schemas import Libro, LibroConId, LibroParcial

app = FastAPI()

libros = []
proximo_id = 1


def buscar_libro(id: int):
    """Busca un libro por su id o lanza 404 si no existe."""
    for libro in libros:
        if libro["id"] == id:
            return libro
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
def listar_libros():
    """Devuelve la lista de libros."""
    return libros


@app.post(
    "/libros",
    status_code=201,
    response_model=LibroConId,
    summary="Crear un libro",
)
def crear_libro(libro: Libro):
    """Crea un nuevo libro y le asigna un id único."""
    global proximo_id
    if existe_libro(libro.titulo, libro.autor):
        raise HTTPException(
            status_code=409,
            detail="Ya existe un libro con el mismo título y autor",
        )
    nuevo = {"id": proximo_id, **libro.model_dump()}
    proximo_id += 1
    libros.append(nuevo)
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
    """Reemplaza todos los campos del libro con ese id."""
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    return libro


@app.patch(
    "/libros/{id}",
    response_model=LibroConId,
    summary="Actualizar parcialmente un libro por id",
)
def actualizar_libro(id: int, datos: LibroParcial):
    """Actualiza solo los campos enviados del libro con ese id."""
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    libro.update(cambios)
    return libro


@app.delete(
    "/libros/{id}",
    status_code=204,
    summary="Eliminar un libro por id",
)
def borrar_libro(id: int):
    """Elimina el libro con ese id. Devuelve 204 sin contenido."""
    libro = buscar_libro(id)
    libros.remove(libro)
