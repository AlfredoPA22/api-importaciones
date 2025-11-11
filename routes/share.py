from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
import secrets
from config.db import db
from schemas.share_token import shareTokenEntity
from schemas.importation import importEntity
from schemas.car import carEntity
from schemas.client import clientEntity
from pydantic import BaseModel

share = APIRouter()

class ShareTokenCreate(BaseModel):
    expires_at: Optional[datetime] = None
    days_valid: Optional[int] = 365  # Días de validez por defecto

def generate_token() -> str:
    """Genera un token único y seguro"""
    return secrets.token_urlsafe(32)

@share.post('/imports/{import_id}/share', status_code=status.HTTP_201_CREATED)
def create_share_token(import_id: str, share_data: Optional[ShareTokenCreate] = None):
    """Genera una URL única para compartir una importación"""
    if not ObjectId.is_valid(import_id):
        raise HTTPException(status_code=400, detail="ID de importación inválido")
    
    # Verificar que la importación exista
    import_item = db.imports.find_one({"_id": ObjectId(import_id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Verificar si ya existe un token activo para esta importación
    existing_token = db.share_tokens.find_one({
        "import_id": import_id,
        "is_active": True
    })
    
    if existing_token:
        # Si existe, desactivar el anterior
        db.share_tokens.update_one(
            {"_id": existing_token["_id"]},
            {"$set": {"is_active": False}}
        )
    
    # Generar nuevo token
    token = generate_token()
    
    # Calcular fecha de expiración
    if share_data and share_data.expires_at:
        expires_at = share_data.expires_at
    elif share_data and share_data.days_valid:
        expires_at = datetime.utcnow() + timedelta(days=share_data.days_valid)
    else:
        expires_at = datetime.utcnow() + timedelta(days=365)
    
    # Crear el token de compartir
    new_token = {
        "import_id": import_id,
        "token": token,
        "expires_at": expires_at,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    result = db.share_tokens.insert_one(new_token)
    created_token = db.share_tokens.find_one({"_id": result.inserted_id})
    
    # Construir la URL de compartir
    # En producción, deberías usar una variable de entorno para la URL base
    base_url = "http://localhost:8000"  # Cambiar en producción
    share_url = f"{base_url}/share/{token}"
    
    return {
        "token": token,
        "share_url": share_url,
        "expires_at": expires_at,
        "is_active": True,
        "import_id": import_id
    }

@share.get('/share/{token}')
def get_import_by_token(token: str):
    """Endpoint público para ver una importación por token (solo muestra costos_cliente)"""
    # Buscar el token
    token_doc = db.share_tokens.find_one({"token": token})
    if not token_doc:
        raise HTTPException(status_code=404, detail="Token no válido o no encontrado")
    
    # Verificar si el token está activo
    if not token_doc.get("is_active", False):
        raise HTTPException(status_code=403, detail="Token desactivado")
    
    # Verificar si el token ha expirado
    expires_at = token_doc.get("expires_at")
    if expires_at and datetime.utcnow() > expires_at:
        raise HTTPException(status_code=403, detail="Token expirado")
    
    # Obtener la importación
    import_id = token_doc.get("import_id")
    import_item = db.imports.find_one({"_id": ObjectId(import_id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    # Construir respuesta (sin costos_reales, solo costos_cliente)
    response = importEntity(import_item, include_real_costs=False)
    
    # Agregar información del auto
    if import_item.get("car_id"):
        car = db.car.find_one({"_id": ObjectId(import_item["car_id"])})
        if car:
            response["car"] = carEntity(car)
    
    # Agregar información básica del cliente (sin datos sensibles)
    if import_item.get("client_id"):
        client = db.clients.find_one({"_id": ObjectId(import_item["client_id"])})
        if client:
            response["client"] = {
                "id": str(client["_id"]),
                "name": client.get("name", ""),
                "company": client.get("company")
            }
    
    return response

@share.delete('/imports/{import_id}/share/{token}')
def deactivate_share_token(import_id: str, token: str):
    """Desactiva un token de compartir"""
    if not ObjectId.is_valid(import_id):
        raise HTTPException(status_code=400, detail="ID de importación inválido")
    
    token_doc = db.share_tokens.find_one({
        "import_id": import_id,
        "token": token
    })
    
    if not token_doc:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    
    db.share_tokens.update_one(
        {"_id": token_doc["_id"]},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Token desactivado correctamente"}

@share.get('/imports/{import_id}/share')
def get_share_tokens(import_id: str):
    """Obtener todos los tokens de compartir de una importación"""
    if not ObjectId.is_valid(import_id):
        raise HTTPException(status_code=400, detail="ID de importación inválido")
    
    import_item = db.imports.find_one({"_id": ObjectId(import_id)})
    if not import_item:
        raise HTTPException(status_code=404, detail="Importación no encontrada")
    
    tokens = db.share_tokens.find({"import_id": import_id}).sort("created_at", -1)
    
    base_url = "http://localhost:8000"  # Cambiar en producción
    tokens_list = []
    for token in tokens:
        token_data = shareTokenEntity(token)
        token_data["share_url"] = f"{base_url}/share/{token['token']}"
        tokens_list.append(token_data)
    
    return tokens_list

