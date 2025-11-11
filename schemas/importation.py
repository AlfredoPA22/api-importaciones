def importEntity(item, include_real_costs: bool = True) -> dict:
    """Serializa una importación. Si include_real_costs es False, solo muestra costos_cliente"""
    result = {
        "id": str(item["_id"]),
        "car_id": item.get("car_id", ""),
        "client_id": item.get("client_id", ""),
        "costos_cliente": item.get("costos_cliente", {}),
        "notes": item.get("notes"),
        "status": item.get("status", "EN_PROCESO"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }
    
    if include_real_costs:
        result["costos_reales"] = item.get("costos_reales", {})
    
    return result

def importsEntity(entity, include_real_costs: bool = True) -> list:
    return [importEntity(item, include_real_costs) for item in entity]

