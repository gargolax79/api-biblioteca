from pydantic import BaseModel


class Libro(BaseModel):
    """Modelo de entrada para un libro."""

    titulo: str
    autor: str
    anio: int
    disponible: bool = True


class LibroConId(Libro):
    """Modelo de salida de un libro con su id asignado."""

    id: int
