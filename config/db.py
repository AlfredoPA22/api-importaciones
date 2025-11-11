from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os

# Configurar timeout para evitar que se quede colgado
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://alfredo:alfredo123@cluster0npm.eqdyu9u.mongodb.net")

# Crear cliente con timeouts
# PyMongo se conecta de forma lazy (solo cuando se necesita)
# Pero configuramos timeouts para que no se quede colgado
conn = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    maxPoolSize=10,
    retryWrites=True
)

db = conn["importaciones-db"]