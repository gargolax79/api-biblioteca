import json
import logging
from pathlib import Path

CARPETA_DATOS = Path(__file__).parent / "datos"
RUTA_ARCHIVO = CARPETA_DATOS / "libros.json"

logger = logging.getLogger(__name__)


def leer_texto_archivo() -> str | None:
    """Devuelve el texto actual de datos/libros.json o None si no existe."""
    try:
        return RUTA_ARCHIVO.read_text(encoding="utf-8")
    except OSError:
        return None


def cargar_libros() -> list[dict]:
    """Carga la lista de libros desde datos/libros.json.

    Si el archivo no existe, está vacío o está dañado, devuelve una lista vacía.
    """
    try:
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if not isinstance(datos, list):
                logger.warning(
                    "El archivo de datos no contiene una lista; iniciando vacío"
                )
                logger.warning("El archivo de datos no contiene una lista; iniciando vacío")
                return []
            datos.sort(key=lambda libro: libro["id"])
            return datos
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError, KeyError, TypeError):
        logger.warning("Archivo de datos vacío o dañado; iniciando con lista vacía")
        return []


def guardar_libros(libros: list[dict]) -> None:
    """Guarda la lista de libros ordenada por id en datos/libros.json."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    libros_ordenados = sorted(libros, key=lambda libro: libro["id"])
    with open(RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(libros_ordenados, archivo, indent=2, ensure_ascii=False)


def calcular_proximo_id(libros: list[dict]) -> int:
    """Calcula el siguiente id como el mayor id guardado + 1 (o 1 si está vacía)."""
    if not libros:
        return 1
    return max(libro["id"] for libro in libros) + 1
