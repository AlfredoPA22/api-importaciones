from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os

# Configurar timeout para evitar que se quede colgado
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://alfredo:alfredo123@cluster0npm.eqdyu9u.mongodb.net")

# Crear cliente con timeouts optimizados para serverless (Vercel)
# PyMongo se conecta de forma lazy (solo cuando se necesita)
# Configuración optimizada para entornos serverless
try:
    conn = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=3000,  # 3 segundos de timeout (más corto para serverless)
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        maxPoolSize=5,  # Pool más pequeño para serverless
        minPoolSize=0,  # No mantener conexiones abiertas
        retryWrites=True,
        retryReads=True,
        # Configuraciones adicionales para serverless
        maxIdleTimeMS=45000,  # Cerrar conexiones inactivas rápido
        heartbeatFrequencyMS=10000
    )
    db = conn["importaciones-db"]
except Exception as e:
    print(f"Advertencia al inicializar MongoDB: {e}")
    # En caso de error, crear una conexión dummy que fallará en el primer uso
    # pero no bloqueará el inicio de la aplicación
    conn = None
    db = None