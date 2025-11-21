from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from routes.car import cars
from routes.importation import imports
from routes.client import clients
from routes.share import share

app = FastAPI(
    title="Sistema de Importaciones API",
    description="API para gestionar autos, clientes, importaciones con costos dinámicos y URLs compartidas",
    version="1.0.0"
)

# Configurar CORS dinámicamente (útil para Vercel)
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    allowed_origins = ["*"]
    allow_credentials = False  # No se permite "*" con credenciales
else:
    allowed_origins = [
        origin.strip()
        for origin in cors_origins_env.split(",")
        if origin.strip()
    ]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz para verificar que la API está funcionando
@app.get("/")
def root():
    return {
        "message": "Sistema de Importaciones API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    # No hacer ping a la base de datos aquí para evitar bloqueos
    # El health check solo verifica que la API esté corriendo
    return {
        "status": "healthy",
        "api": "running"
    }

# Incluir routers primero (antes de montar archivos estáticos)
app.include_router(cars, tags=["Autos"])
app.include_router(clients, tags=["Clientes"])
app.include_router(imports, tags=["Importaciones"])
app.include_router(share, tags=["Compartir"])

# Detectar si estamos en Vercel (serverless)
IS_VERCEL = os.getenv("VERCEL") == "1"

# Solo montar archivos estáticos si NO estamos en Vercel
# En Vercel, los archivos estáticos deben manejarse de otra forma (S3, Cloudinary, etc.)
if not IS_VERCEL:
    # Montar directorio de archivos estáticos para imágenes (al final)
    # Crear estructura de directorios
    uploads_base = Path("uploads")
    uploads_imports = Path("uploads/imports")
    try:
        uploads_base.mkdir(exist_ok=True)
        uploads_imports.mkdir(parents=True, exist_ok=True)
        
        # Montar archivos estáticos solo si el directorio existe
        if uploads_base.exists():
            app.mount("/uploads", StaticFiles(directory=str(uploads_base)), name="uploads")
    except Exception as e:
        print(f"Advertencia: No se pudo montar directorio de uploads: {e}")
else:
    print("Modo Vercel detectado: los archivos estáticos no se montarán localmente")