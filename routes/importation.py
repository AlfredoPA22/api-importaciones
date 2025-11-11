from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from config.db import db
from schemas.importation import importEntity, importsEntity
from schemas.car import carEntity
from schemas.client import clientEntity
from models.importation import Import, ImportUpdate

imports = APIRouter()

@imports.get('/imports')
def list_imports():
    return importsEntity(db.imports.find())

@imports.post('/imports', status_code=status.HTTP_201_CREATED)
def create_import(import_data: Import):
    # Verificar que el auto exista
    if not ObjectId.is_valid(import_data.car_id):
        raise HTTPException(status_code=400, detail="ID de auto inválido")
    
    car = db.car.find_one({"_id": ObjectId(import_data.car_id)})
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    # Verificar que el auto no esté ya asociado a otra importación
    existing_import = db.imports.find_one({"car_id": import_data.car_id})
    if existing_import:
        raise HTTPException(
            status_code=409,
            detail=f"El auto ya está asociado a una importación (ID: {existing_import['_id']}). Un auto solo puede pertenecer a una importación."
        )
    
    # Verificar que el cliente exista
    if not ObjectId.is_valid(import_data.client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")
    
    client = db.clients.find_one({"_id": ObjectId(import_data.client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Crear la importación
    new_import = {
        "car_id": import_data.car_id,
        "client_id": import_data.client_id,
        "costos_reales": import_data.costos_reales,
        "costos_cliente": import_data.costos_cliente,
        "notes": import_data.notes,
        "status": import_data.status.value if import_data.status else "EN_PROCESO",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.imports.insert_one(new_import)
    created_import = db.imports.find_one({"_id": result.inserted_id})
    
    response = importEntity(created_import)
    response["car"] = carEntity(car)
    response["client"] = clientEntity(client)
    
    return response

@imports.get('/imports/{id}')
def detail_import(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    import_item = db.imports.find_one({"_id": ObjectId(id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Obtener información del auto y cliente
    response = importEntity(import_item)
    if import_item.get("car_id"):
        car = db.car.find_one({"_id": ObjectId(import_item["car_id"])})
        if car:
            response["car"] = carEntity(car)
    
    if import_item.get("client_id"):
        client = db.clients.find_one({"_id": ObjectId(import_item["client_id"])})
        if client:
            response["client"] = clientEntity(client)
    
    return response

@imports.put('/imports/{id}')
def update_import(id: str, import_update: ImportUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que la importación exista
    import_item = db.imports.find_one({"_id": ObjectId(id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Preparar datos de actualización
    update_data = {}
    
    # Si se envían costos reales, fusionarlos con los existentes
    if import_update.costos_reales is not None:
        existing_costs_reales = import_item.get("costos_reales", {})
        existing_costs_reales.update(import_update.costos_reales)
        update_data["costos_reales"] = existing_costs_reales
    
    # Si se envían costos cliente, fusionarlos con los existentes
    if import_update.costos_cliente is not None:
        existing_costs_cliente = import_item.get("costos_cliente", {})
        existing_costs_cliente.update(import_update.costos_cliente)
        update_data["costos_cliente"] = existing_costs_cliente
    
    if import_update.notes is not None:
        update_data["notes"] = import_update.notes
    
    if import_update.status is not None:
        update_data["status"] = import_update.status.value
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    update_data["updated_at"] = datetime.utcnow()
    
    db.imports.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    updated_import = db.imports.find_one({"_id": ObjectId(id)})
    response = importEntity(updated_import)
    
    # Incluir información del auto y cliente
    if updated_import.get("car_id"):
        car = db.car.find_one({"_id": ObjectId(updated_import["car_id"])})
        if car:
            response["car"] = carEntity(car)
    
    if updated_import.get("client_id"):
        client = db.clients.find_one({"_id": ObjectId(updated_import["client_id"])})
        if client:
            response["client"] = clientEntity(client)
    
    return response

@imports.delete('/imports/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_import(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = db.imports.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    return None

@imports.get('/imports/car/{car_id}')
def get_import_by_car(car_id: str):
    """Obtener la importación de un auto específico (un auto solo puede tener una importación)"""
    if not ObjectId.is_valid(car_id):
        raise HTTPException(status_code=400, detail="ID de auto inválido")
    
    car = db.car.find_one({"_id": ObjectId(car_id)})
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    import_item = db.imports.find_one({"car_id": car_id})
    if not import_item:
        raise HTTPException(status_code=404, detail="El auto no tiene una importación asociada")
    
    response = importEntity(import_item)
    response["car"] = carEntity(car)
    
    # Agregar información del cliente
    if import_item.get("client_id"):
        client = db.clients.find_one({"_id": ObjectId(import_item["client_id"])})
        if client:
            response["client"] = clientEntity(client)
    
    return response

@imports.get('/imports/client/{client_id}')
def get_imports_by_client(client_id: str):
    """Obtener todas las importaciones de un cliente específico"""
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")
    
    client = db.clients.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    imports_list = db.imports.find({"client_id": client_id})
    return importsEntity(imports_list)

