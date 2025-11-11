from typing import Dict, Optional
from pydantic import BaseModel, Field
from utils.statusEnum import CarStatus

class Import(BaseModel):
    car_id: str
    client_id: str
    costos_reales: Dict[str, float] = Field(default_factory=dict, description="Costos reales internos (solo administrador)")
    costos_cliente: Dict[str, float] = Field(default_factory=dict, description="Costos que verá el cliente")
    notes: Optional[str] = None
    status: Optional[CarStatus] = CarStatus.EN_PROCESO

class ImportUpdate(BaseModel):
    costos_reales: Optional[Dict[str, float]] = None
    costos_cliente: Optional[Dict[str, float]] = None
    notes: Optional[str] = None
    status: Optional[CarStatus] = None

