from typing import Optional
from pydantic import BaseModel, Field


class Libro(BaseModel):
    """Modelo de entrada para crear o reemplazar un libro."""

    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True


class LibroConId(Libro):
    """Modelo de salida de un libro con su id asignado."""

    id: int


class LibroParcial(BaseModel):
    """Modelo para actualizar parcialmente un libro (PATCH)."""

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=100)
    autor: Optional[str] = Field(default=None, min_length=3, max_length=60)
    anio: Optional[int] = Field(default=None, ge=1000, le=2100)
    disponible: Optional[bool] = None
