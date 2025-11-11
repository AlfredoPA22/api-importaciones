from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.car import cars
from routes.importation import imports
from routes.client import clients
from routes.share import share

app = FastAPI(
    title="Sistema de Importaciones API",
    description="API para gestionar autos, clientes, importaciones con costos dinámicos y URLs compartidas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
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
    try:
        from config.db import db
        # Intentar hacer un ping a la base de datos
        db.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

app.include_router(cars, tags=["Autos"])
app.include_router(clients, tags=["Clientes"])
app.include_router(imports, tags=["Importaciones"])
app.include_router(share, tags=["Compartir"])