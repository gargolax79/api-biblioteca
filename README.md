# API de la Biblioteca (`api-biblioteca`)

API REST construida con **FastAPI** y **Pydantic** para gestionar el catálogo de libros de una biblioteca (crear, listar, buscar, filtrar, paginar, actualizar, prestar, devolver y eliminar libros), con persistencia automática en archivo JSON (`datos/libros.json`).

## Instalar

1. Clonar el repositorio y entrar a la carpeta del proyecto:
   ```bash
   git clone https://github.com/gargolax79/api-biblioteca.git
   cd api-biblioteca
   ```
2. Crear y activar el entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instalar las dependencias con `pip install`:
   ```bash
   pip install -r requirements.txt
   ```

## Correr

Levantar el servidor de desarrollo con FastAPI o Uvicorn desde la raíz del proyecto:

```bash
fastapi dev main.py
```

O alternativamente con Uvicorn:

```bash
uvicorn main:app --reload
```

Una vez iniciado el servidor, la documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.
