from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from utils.statusEnum import CarStatus

class StatusHistory(BaseModel):
    status: str
    changed_at: datetime
    notes: Optional[str] = None

class Import(BaseModel):
    car_id: str
    client_id: str
    costos_reales: Dict[str, float] = Field(default_factory=dict, description="Costos reales internos (solo administrador)")
    costos_cliente: Dict[str, float] = Field(default_factory=dict, description="Costos que verá el cliente")
    notes: Optional[str] = None
    status: Optional[CarStatus] = CarStatus.EN_PROCESO
    fecha_tentativa_entrega: Optional[datetime] = Field(None, description="Fecha tentativa de entrega del vehículo")
    images: Optional[List[str]] = Field(default_factory=list, description="Lista de URLs de imágenes de la importación")

class ImportUpdate(BaseModel):
    costos_reales: Optional[Dict[str, Optional[float]]] = Field(None, description="Costos reales a agregar/actualizar. Use null para eliminar un costo específico.")
    costos_cliente: Optional[Dict[str, Optional[float]]] = Field(None, description="Costos cliente a agregar/actualizar. Use null para eliminar un costo específico.")
    costos_reales_to_delete: Optional[List[str]] = Field(None, description="Lista de nombres de costos reales a eliminar")
    costos_cliente_to_delete: Optional[List[str]] = Field(None, description="Lista de nombres de costos cliente a eliminar")
    notes: Optional[str] = None
    status: Optional[CarStatus] = None
    fecha_tentativa_entrega: Optional[datetime] = Field(None, description="Fecha tentativa de entrega del vehículo")

