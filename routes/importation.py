from fastapi import APIRouter, HTTPException, status, UploadFile, File
from bson import ObjectId
from datetime import datetime
import uuid
from pathlib import Path
from config.db import db
from schemas.importation import importEntity, importsEntity
from schemas.car import carEntity
from schemas.client import clientEntity
from models.importation import Import, ImportUpdate

imports = APIRouter()

# Configurar directorio para imágenes
UPLOAD_DIR = Path("uploads/imports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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
    initial_status = import_data.status.value if import_data.status else "EN_PROCESO"
    now = datetime.utcnow()
    
    new_import = {
        "car_id": import_data.car_id,
        "client_id": import_data.client_id,
        "costos_reales": import_data.costos_reales,
        "costos_cliente": import_data.costos_cliente,
        "notes": import_data.notes,
        "status": initial_status,
        "fecha_tentativa_entrega": import_data.fecha_tentativa_entrega,
        "images": import_data.images or [],
        "status_history": [
            {
                "status": initial_status,
                "changed_at": now,
                "notes": "Importación creada"
            }
        ],
        "created_at": now,
        "updated_at": now
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
    
    # Manejar costos reales
    if import_update.costos_reales is not None or import_update.costos_reales_to_delete is not None:
        existing_costs_reales = import_item.get("costos_reales", {}).copy()
        
        # Primero, eliminar costos especificados en la lista
        if import_update.costos_reales_to_delete:
            for costo_name in import_update.costos_reales_to_delete:
                existing_costs_reales.pop(costo_name, None)
        
        # Luego, agregar/actualizar/eliminar costos del diccionario
        if import_update.costos_reales is not None:
            for costo_name, costo_value in import_update.costos_reales.items():
                if costo_value is None:
                    # Si el valor es None, eliminar el costo
                    existing_costs_reales.pop(costo_name, None)
                else:
                    # Si tiene valor, agregar o actualizar
                    existing_costs_reales[costo_name] = costo_value
        
        update_data["costos_reales"] = existing_costs_reales
    
    # Manejar costos cliente
    if import_update.costos_cliente is not None or import_update.costos_cliente_to_delete is not None:
        existing_costs_cliente = import_item.get("costos_cliente", {}).copy()
        
        # Primero, eliminar costos especificados en la lista
        if import_update.costos_cliente_to_delete:
            for costo_name in import_update.costos_cliente_to_delete:
                existing_costs_cliente.pop(costo_name, None)
        
        # Luego, agregar/actualizar/eliminar costos del diccionario
        if import_update.costos_cliente is not None:
            for costo_name, costo_value in import_update.costos_cliente.items():
                if costo_value is None:
                    # Si el valor es None, eliminar el costo
                    existing_costs_cliente.pop(costo_name, None)
                else:
                    # Si tiene valor, agregar o actualizar
                    existing_costs_cliente[costo_name] = costo_value
        
        update_data["costos_cliente"] = existing_costs_cliente
    
    if import_update.notes is not None:
        update_data["notes"] = import_update.notes
    
    # Manejar cambio de estado y registrar en historial
    if import_update.status is not None:
        new_status = import_update.status.value
        current_status = import_item.get("status", "EN_PROCESO")
        
        # Solo registrar en historial si el estado cambió
        if new_status != current_status:
            update_data["status"] = new_status
            
            # Obtener historial existente o crear uno nuevo
            status_history = import_item.get("status_history", [])
            
            # Agregar nuevo registro al historial
            status_history.append({
                "status": new_status,
                "changed_at": datetime.utcnow(),
                "notes": f"Cambio de estado de {current_status} a {new_status}"
            })
            
            update_data["status_history"] = status_history
        else:
            # Si es el mismo estado, solo actualizar
            update_data["status"] = new_status
    
    if import_update.fecha_tentativa_entrega is not None:
        update_data["fecha_tentativa_entrega"] = import_update.fecha_tentativa_entrega
    
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

@imports.get('/imports/{id}/history')
def get_import_history(id: str):
    """Obtener el historial de estados de una importación (timeline)"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    import_item = db.imports.find_one({"_id": ObjectId(id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    from schemas.importation import statusHistoryEntityList
    
    # Obtener historial y ordenarlo por fecha (más antiguo primero para timeline)
    status_history = import_item.get("status_history", [])
    
    # Si no hay historial pero hay un estado, crear un registro inicial
    if not status_history and import_item.get("status"):
        status_history = [{
            "status": import_item.get("status", "EN_PROCESO"),
            "changed_at": import_item.get("created_at", datetime.utcnow()),
            "notes": "Estado inicial"
        }]
    
    # Ordenar por fecha (más antiguo primero para timeline)
    status_history_sorted = sorted(
        status_history,
        key=lambda x: x.get("changed_at", datetime.utcnow()),
        reverse=False
    )
    
    return {
        "import_id": str(import_item["_id"]),
        "current_status": import_item.get("status", "EN_PROCESO"),
        "fecha_tentativa_entrega": import_item.get("fecha_tentativa_entrega"),
        "history": statusHistoryEntityList(status_history_sorted)
    }

@imports.post('/imports/{id}/images', status_code=status.HTTP_201_CREATED)
async def upload_image(id: str, file: UploadFile = File(...)):
    """Subir una imagen a una importación"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que la importación exista
    import_item = db.imports.find_one({"_id": ObjectId(id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Validar extensión del archivo
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamaño del archivo
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Generar nombre único para el archivo
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    # Guardar archivo
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")
    
    # Generar URL de la imagen
    image_url = f"/uploads/imports/{filename}"
    
    # Agregar imagen a la importación
    images = import_item.get("images", [])
    images.append(image_url)
    
    db.imports.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "images": images,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Imagen subida correctamente",
        "image_url": image_url,
        "filename": filename
    }

@imports.delete('/imports/{id}/images/{filename}')
def delete_image(id: str, filename: str):
    """Eliminar una imagen de una importación"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    # Verificar que la importación exista
    import_item = db.imports.find_one({"_id": ObjectId(id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Construir URL y ruta del archivo
    image_url = f"/uploads/imports/{filename}"
    file_path = UPLOAD_DIR / filename
    
    # Verificar que la imagen esté en la lista de imágenes de la importación
    images = import_item.get("images", [])
    if image_url not in images:
        raise HTTPException(status_code=404, detail="Imagen no encontrada en esta importación")
    
    # Eliminar archivo del sistema de archivos
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")
    
    # Eliminar imagen de la lista
    images.remove(image_url)
    
    db.imports.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "images": images,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Imagen eliminada correctamente"}


