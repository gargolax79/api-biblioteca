from fastapi import FastAPI
from schemas import Libro, LibroConId

app = FastAPI()

libros = []
proximo_id = 1


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
