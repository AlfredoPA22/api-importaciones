def statusHistoryEntity(item) -> dict:
    """Serializa un elemento del historial de estados"""
    return {
        "status": item.get("status", ""),
        "changed_at": item.get("changed_at"),
        "notes": item.get("notes"),
    }

def statusHistoryEntityList(history_list) -> list:
    """Serializa una lista de historial de estados"""
    return [statusHistoryEntity(item) for item in history_list]

def importEntity(item, include_real_costs: bool = True) -> dict:
    """Serializa una importación. Si include_real_costs es False, solo muestra costos_cliente"""
    result = {
        "id": str(item["_id"]),
        "car_id": item.get("car_id", ""),
        "client_id": item.get("client_id", ""),
        "costos_cliente": item.get("costos_cliente", {}),
        "notes": item.get("notes"),
        "status": item.get("status", "EN_PROCESO"),
        "fecha_tentativa_entrega": item.get("fecha_tentativa_entrega"),
        "images": item.get("images", []),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }
    
    if include_real_costs:
        result["costos_reales"] = item.get("costos_reales", {})
    
    # Incluir historial de estados si existe
    if "status_history" in item:
        result["status_history"] = statusHistoryEntityList(item.get("status_history", []))
    
    return result

def importsEntity(entity, include_real_costs: bool = True) -> list:
    return [importEntity(item, include_real_costs) for item in entity]

