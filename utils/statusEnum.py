from enum import Enum

class CarStatus(str, Enum):
    EN_PROCESO = "EN_PROCESO"
    EN_TRANSITO = "EN_TRANSITO"
    EN_TALLER = "EN_TALLER"
    EN_ADUANA = "EN_ADUANA"
    ENTREGADO = "ENTREGADO"
