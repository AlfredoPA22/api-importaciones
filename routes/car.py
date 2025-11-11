from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from config.db import db
from schemas.car import carEntity, carsEntity
from models.car import Car, CarUpdate

cars = APIRouter()

@cars.get('/cars')
def list_cars():
    cars_list = list(db.car.find())
    result = []
    
    for car in cars_list:
        car_data = carEntity(car)
        # Verificar si el auto tiene una importación asociada
        car_id_str = str(car["_id"])
        import_item = db.imports.find_one({"car_id": car_id_str})
        if import_item:
            car_data["has_import"] = True
            car_data["import_id"] = str(import_item["_id"])
            car_data["can_create_import"] = False
        else:
            car_data["has_import"] = False
            car_data["import_id"] = None
            car_data["can_create_import"] = True
        result.append(car_data)
    
    return result

@cars.post('/cars', status_code=status.HTTP_201_CREATED)
def create_car(car: Car):
    new_car = dict(car)
    result = db.car.insert_one(new_car)
    
    created_car = db.car.find_one({"_id": result.inserted_id})
    return carEntity(created_car)

@cars.get('/cars/{id}')
def detail_car(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    car = db.car.find_one({"_id": ObjectId(id)})
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    # Agregar información sobre importación asociada (un auto solo puede tener una)
    response = carEntity(car)
    import_item = db.imports.find_one({"car_id": id})
    
    if import_item:
        response["has_import"] = True
        response["import_id"] = str(import_item["_id"])
        response["can_delete"] = False
        response["can_create_import"] = False
    else:
        response["has_import"] = False
        response["import_id"] = None
        response["can_delete"] = True
        response["can_create_import"] = True
    
    return response

@cars.put('/cars/{id}')
def update_car(id: str, car_update: CarUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que el auto exista
    car = db.car.find_one({"_id": ObjectId(id)})
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    # Filtrar solo los campos que no son None
    update_data = {k: v for k, v in car_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    db.car.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    
    updated_car = db.car.find_one({"_id": ObjectId(id)})
    return carEntity(updated_car)

@cars.delete('/cars/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_car(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que el auto exista
    car = db.car.find_one({"_id": ObjectId(id)})
    if not car:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    # Verificar si el auto está asociado a una importación
    import_item = db.imports.find_one({"car_id": id})
    if import_item:
        raise HTTPException(
            status_code=409,
            detail=f"No se puede eliminar el auto porque está asociado a una importación (ID: {import_item['_id']}). Elimine primero la importación asociada."
        )
    
    result = db.car.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    return None

