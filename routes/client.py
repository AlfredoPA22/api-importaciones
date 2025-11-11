from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from config.db import db
from schemas.client import clientEntity, clientsEntity
from models.client import Client, ClientUpdate

clients = APIRouter()

@clients.get('/clients')
def list_clients():
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    return clientsEntity(db.clients.find())

@clients.post('/clients', status_code=status.HTTP_201_CREATED)
def create_client(client: Client):
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    new_client = dict(client)
    new_client["created_at"] = datetime.utcnow()
    new_client["updated_at"] = datetime.utcnow()
    
    result = db.clients.insert_one(new_client)
    created_client = db.clients.find_one({"_id": result.inserted_id})
    return clientEntity(created_client)

@clients.get('/clients/{id}')
def detail_client(id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    client = db.clients.find_one({"_id": ObjectId(id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Agregar información sobre importaciones asociadas
    response = clientEntity(client)
    import_count = db.imports.count_documents({"client_id": id})
    response["import_count"] = import_count
    response["can_delete"] = import_count == 0
    
    return response

@clients.put('/clients/{id}')
def update_client(id: str, client_update: ClientUpdate):
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    client = db.clients.find_one({"_id": ObjectId(id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    update_data = {k: v for k, v in client_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    update_data["updated_at"] = datetime.utcnow()
    
    db.clients.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    updated_client = db.clients.find_one({"_id": ObjectId(id)})
    return clientEntity(updated_client)

@clients.delete('/clients/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_client(id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que el cliente exista
    client = db.clients.find_one({"_id": ObjectId(id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar si el cliente está asociado a alguna importación
    import_count = db.imports.count_documents({"client_id": id})
    if import_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"No se puede eliminar el cliente porque está asociado a {import_count} importación(es). Elimine primero las importaciones asociadas."
        )
    
    result = db.clients.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return None

