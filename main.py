from fastapi import FastAPI, HTTPException
from schemas import Libro, LibroConId

app = FastAPI()

libros = []
proximo_id = 1


def buscar_libro(id: int):
    """Busca un libro por su id o lanza 404 si no existe."""
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail=f"No existe el libro con id {id}")


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


@app.delete(
    "/libros/{id}",
    status_code=204,
    summary="Eliminar un libro por id",
)
def borrar_libro(id: int):
    """Elimina el libro con ese id. Devuelve 204 sin contenido."""
    libro = buscar_libro(id)
    libros.remove(libro)

