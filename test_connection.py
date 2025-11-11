"""
Script para probar la conexión a MongoDB
"""
import sys
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

MONGODB_URL = "mongodb+srv://alfredo:alfredo123@cluster0npm.eqdyu9u.mongodb.net"

print("Intentando conectar a MongoDB...")
try:
    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    # Probar conexión
    client.admin.command('ping')
    print("✓ Conexión exitosa a MongoDB")
    
    # Listar bases de datos
    dbs = client.list_database_names()
    print(f"✓ Bases de datos disponibles: {dbs}")
    
    # Probar acceso a la base de datos
    db = client["importaciones-db"]
    collections = db.list_collection_names()
    print(f"✓ Colecciones en 'importaciones-db': {collections}")
    
except ServerSelectionTimeoutError as e:
    print(f"✗ Error: No se pudo conectar a MongoDB (timeout)")
    print(f"  Detalles: {e}")
    sys.exit(1)
except ConnectionFailure as e:
    print(f"✗ Error: Fallo de conexión a MongoDB")
    print(f"  Detalles: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error inesperado: {e}")
    sys.exit(1)

print("\n✓ Todo funciona correctamente")

